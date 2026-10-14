param(
    [string]$SwissDll = 'C:\Program Files (x86)\Jagannatha Hora\bin\swedll32.dll',
    [string]$EphemerisPath = 'C:\Program Files (x86)\Jagannatha Hora\jhcore\ephe'
)
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding $false
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
if ([IntPtr]::Size -ne 4) { throw 'Use 32-bit Windows PowerShell for this DLL.' }
$taskSha = [System.Security.Cryptography.SHA256]::Create()
$taskHash = [BitConverter]::ToString($taskSha.ComputeHash([IO.File]::ReadAllBytes($SwissDll))).Replace('-','').ToLowerInvariant()
$taskSha.Dispose()
if ($taskHash -ne 'd56ba3a6158fcec3921774b5c9fcc533374413d7b77cdbc6b83ffa082d260a69') {
    throw 'The Swiss DLL differs from the verified JHora 8.0 DLL.'
}
$taskSource = @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class JHoraSwiss {
    [DllImport(@"DLL_PATH", EntryPoint="_swe_set_ephe_path@4", CallingConvention=CallingConvention.StdCall, CharSet=CharSet.Ansi)]
    public static extern void SetPath(string path);
    [DllImport(@"DLL_PATH", EntryPoint="_swe_calc@24", CallingConvention=CallingConvention.StdCall, CharSet=CharSet.Ansi)]
    private static extern int Calc(double tt, int planet, int flags, [Out] double[] xx, StringBuilder error);
    [DllImport(@"DLL_PATH", EntryPoint="_swe_deltat@8", CallingConvention=CallingConvention.StdCall)]
    public static extern double DeltaT(double ut);
    [DllImport(@"DLL_PATH", EntryPoint="_swe_fixstar@24", CallingConvention=CallingConvention.StdCall, CharSet=CharSet.Ansi)]
    private static extern int FixStar(StringBuilder star, double tt, int flags, [Out] double[] xx, StringBuilder error);
    [DllImport(@"DLL_PATH", EntryPoint="_swe_houses@36", CallingConvention=CallingConvention.StdCall)]
    private static extern int Houses(double ut,double latitude,double longitude,int code,[Out] double[] cusps,[Out] double[] ascmc);
    [DllImport(@"DLL_PATH", EntryPoint="_swe_rise_trans@52", CallingConvention=CallingConvention.StdCall, CharSet=CharSet.Ansi)]
    private static extern int Rise(double ut,int planet,StringBuilder star,int flags,int rsmi,double[] geo,double pressure,double temperature,[Out] double[] times,StringBuilder error);
    public static double Norm(double value) { return (value % 360 + 360) % 360; }
    public static double[] Star(double ut,int flags) {
        double[] xx=new double[6]; var error=new StringBuilder(1024);
        if(FixStar(new StringBuilder("Spica",1024),ut+DeltaT(ut),flags & ~65536,xx,error)<0) throw new Exception(error.ToString());
        return xx;
    }
    public static double[] Position(double ut,int planet,int flags) {
        double[] xx=new double[6]; var error=new StringBuilder(1024);
        if(Calc(ut+DeltaT(ut),planet,flags & ~65536,xx,error)<0) throw new Exception(error.ToString());
        if((flags & 65536)!=0) xx[0]=Norm(xx[0]-Star(ut,flags)[0]+180);
        return xx;
    }
    public static double[] Ascendant(double ut,double lat,double lon) {
        double[] cusps=new double[13], ascmc=new double[10];
        if(Houses(ut,lat,lon,69,cusps,ascmc)<0) throw new Exception("Swiss houses calculation failed");
        double meanAyan=Star(ut,2+16+64)[0]-180;
        return new double[] {Norm(ascmc[0]-meanAyan),ascmc[0],meanAyan};
    }
    public static double RiseTime(double ut,int planet,int flags,int rsmi,double lat,double lon,double altitude) {
        double[] times=new double[10]; var error=new StringBuilder(1024);
        int result=Rise(ut,planet,new StringBuilder("",1024),flags,rsmi,new double[]{lon,lat,altitude},0,0,times,error);
        if(result<0) throw new Exception("Rise/set unavailable: "+error.ToString());
        return times[0];
    }
    public static double SolarDate(double birth,double years,int flags) {
        double target=Norm(Position(birth,0,flags)[0]+years*360);
        double trial=birth+years*365.256364;
        for(int i=0;i<40;i++) {
            double[] pos=Position(trial,0,flags);
            double step=(Norm(pos[0]-target+180)-180)/pos[3];
            trial-=step;
            if(Math.Abs(step)<1e-9) return trial;
        }
        throw new Exception("Solar arc root did not converge");
    }
}
'@.Replace('DLL_PATH',$SwissDll.Replace('"','""'))
Add-Type -TypeDefinition $taskSource
[JHoraSwiss]::SetPath($EphemerisPath)
[Console]::Out.WriteLine('{"ready":true,"engine":"Swiss Ephemeris 2.02.01"}')
while ($null -ne ($taskLine = [Console]::In.ReadLine())) {
    try {
        $taskRequest = $taskLine | ConvertFrom-Json
        $taskResult = switch ($taskRequest.op) {
            'position' { ,([JHoraSwiss]::Position($taskRequest.ut,$taskRequest.planet,$taskRequest.flags)) }
            'star' { ,([JHoraSwiss]::Star($taskRequest.ut,$taskRequest.flags)) }
            'ascendant' { ,([JHoraSwiss]::Ascendant($taskRequest.ut,$taskRequest.latitude,$taskRequest.longitude)) }
            'rise' { [JHoraSwiss]::RiseTime($taskRequest.ut,$taskRequest.planet,$taskRequest.flags,$taskRequest.rsmi,$taskRequest.latitude,$taskRequest.longitude,$taskRequest.altitude) }
            'solar' { [JHoraSwiss]::SolarDate($taskRequest.birth,$taskRequest.years,$taskRequest.flags) }
            'delta_t' { [JHoraSwiss]::DeltaT($taskRequest.ut) }
            'stop' { break }
            default { throw 'Unknown calculation operation' }
        }
        [Console]::Out.WriteLine((@{result=$taskResult} | ConvertTo-Json -Compress -Depth 5))
    } catch {
        [Console]::Out.WriteLine((@{error=$_.Exception.Message} | ConvertTo-Json -Compress))
    }
    if ($taskRequest.op -eq 'stop') { break }
}
