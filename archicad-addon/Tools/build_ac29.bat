@echo off
REM AC29-only build (the stock build_all_win.bat builds 25-29; we only need 29).
REM Assumes the AC29 DevKit is already in ..\Build\DevKits\AC29 and VS 2026
REM Build Tools (v143) + CMake are installed.
pushd %~dp0

cmake -B ../Build/AC29 -G "Visual Studio 18 2026" -A "x64" -T "v143" -DAC_VERSION=29 -DAC_API_DEVKIT_DIR="..\Build\DevKits\AC29\Support" .. || goto :error
cmake --build ../Build/AC29 --config RelWithDebInfo || goto :error

popd
echo Build OK.
exit /b 0

:error
echo Build Failed with Error %errorlevel%.
popd
exit /b 1
