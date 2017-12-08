# PowerShell Wrapper for MDT, Standalone, Chocolatey and LifeCycle Management - (C)2015 xenappblog.com 

# Example 1: Start-Process "XenDesktopServerSetup.exe" -ArgumentList $unattendedArgs -Wait -Passthru
# Example 2 Powershell: Start-Process powershell.exe -ExecutionPolicy bypass -file $Destination

# Example 3 EXE (Always use ' '):
# $UnattendedArgs='/qn'
# (Start-Process "$PackageName.$InstallerType" $UnattendedArgs -Wait -Passthru).ExitCode

# Example 4 MSI (Always use " "):
# $UnattendedArgs = "/i $PackageName.$InstallerType ALLUSERS=1 /qn /liewa $LogApp"
# (Start-Process msiexec.exe -ArgumentList $UnattendedArgs -Wait -Passthru).ExitCode

Write-Verbose "Setting Arguments" -Verbose
$startDTM = (Get-Date)

$Vendor = "Liquidware Labs"
$Product = "ProfileUnity"
$Version = "6.5"
$PackageName = "ProfileUnity-Net_6.5gab1"
$InstallerType = "exe"
$LogPS = "${env:SystemRoot}" + "\Temp\$Vendor $PackageName PS Wrapper.log"
$LogApp = "${env:SystemRoot}" + "\Temp\$PackageName.log"
$UnattendedArgs = '/exelang 1033 /exenoui IAgree=Yes USER_PASSWORD=P@ssw0rd USER_PASSWORD_1=P@ssw0rd ALLUSERS=1 /qn /norestart'
$url = "http://software.liquidwarelabs.com/6.5.0/" + "$PackageName.$InstallerType"
$output = "$env:SystemDrive\Installers\$Vendor\$Product\$Version\$PackageName.$InstallerType"

Start-Transcript $LogPS

                if (-not (Test-Path $output)) {
        New-Item -Path $env:SystemDrive\Installers\$Vendor\$Product\$Version -ItemType Directory -Force
                                Write-Verbose "Starting Download of $Vendor $Product $Version" -Verbose
                                $wc = New-Object System.Net.WebClient
                                $wc.DownloadFile($url, $output)
                                start-sleep -s 10
                                }
                else
                                {Write-Verbose "$Vendor $PackageName Exist" -Verbose}         

CD $env:SystemDrive\Installers\$Vendor\$Product\$Version

Write-Verbose "Starting Installation of $Vendor $Product $Version" -Verbose 
(Start-Process "$PackageName.$InstallerType" $UnattendedArgs)
Start-Sleep -s 300

Write-Verbose "Customization" -Verbose

Write-Verbose "Stop logging" -Verbose
$EndDTM = (Get-Date)
Write-Verbose "Elapsed Time: $(($EndDTM-$StartDTM).TotalSeconds) Seconds" -Verbose
Write-Verbose "Elapsed Time: $(($EndDTM-$StartDTM).TotalMinutes) Minutes" -Verbose
Stop-Transcript
