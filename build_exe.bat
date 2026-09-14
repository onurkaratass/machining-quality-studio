@echo off
chcp 65001 > nul
echo =======================================================================
echo   Machining & Quality Studio (.exe) Windows Derleyicisi
echo =======================================================================
echo.

set "PY_CMD="

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_FOUND
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py"
    goto :PYTHON_FOUND
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :PYTHON_FOUND
    )
)

for /d %%D in ("C:\Program Files\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :PYTHON_FOUND
    )
)

:PYTHON_NOT_FOUND
echo [HATA] Bilgisayarinizda Python bulunamadi!
echo Lutfen https://www.python.org/downloads/ adresinden Python'i indirin ve
echo "Add python.exe to PATH" secenegini isaretleyerek kurun.
pause
exit /b 1

:PYTHON_FOUND
echo [+] Python bulundu: %PY_CMD%
echo.
echo [1/3] Kutuphaneler kontrol ediliyor ve yukleniyor...
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install -r requirements.txt
%PY_CMD% -m pip install pyinstaller customtkinter

echo.
echo [2/3] Standalone Windows EXE paketi derleniyor (Lutfen bekleyin)...
%PY_CMD% -m PyInstaller --noconfirm --onefile --windowed --collect-all customtkinter --icon "assets\icon.ico" --add-data "assets;assets" --name "Machining_Quality_Studio" main.py

echo.
echo =======================================================================
if exist "dist\Machining_Quality_Studio.exe" (
    echo [3/3] BASARILI: dist\Machining_Quality_Studio.exe olusturuldu!
    echo       Artik bu uygulamayi cift tiklayarak dogrudan kullanabilirsiniz.
) else (
    echo [HATA] Derleme sirasinda bir hata meydana geldi.
)
echo =======================================================================
pause
