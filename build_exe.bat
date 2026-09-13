@echo off
chcp 65001 > nul
echo ========================================================
echo   SPC Analiz ve Kalite Kontrol Uygulamasi (.exe) Derleyici
echo ========================================================
echo.

:: 1. Python çalıştırıcısını tespit et (python, py veya AppData konumu)
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
echo.
echo Cozum:
echo 1. https://www.python.org/downloads/ adresinden Python'i indirin.
echo 2. Kurulum ekraninin EN ALTINDA yer alan:
echo    "[X] Add python.exe to PATH" secenegini KESINLIKLE isaretleyin.
echo 3. Kurulum tamamlandiktan sonra bu dosyayi (build_exe.bat) tekrar calistirin.
echo ========================================================
pause
exit /b 1

:PYTHON_FOUND
echo [+] Python bulundu: %PY_CMD%
echo.
echo [1/3] Gerekli kutuphaneler kontrol ediliyor ve yukleniyor...
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install -r requirements.txt
%PY_CMD% -m pip install pyinstaller

echo.
echo [2/3] Standalone Windows EXE paketi derleniyor (lutfen bekleyin)...
%PY_CMD% -m PyInstaller --noconfirm --onefile --windowed --name "SPC_Quality_Analyzer" app_gui.py

echo.
echo ========================================================
if exist "dist\SPC_Quality_Analyzer.exe" (
    echo [3/3] BASARILI: dist\SPC_Quality_Analyzer.exe olusturuldu!
    echo       dist klasorundeki bu .exe dosyasini cift tiklayarak kullanabilirsiniz.
) else (
    echo [HATA] Derleme sirasinda bir sorun olustu.
)
echo ========================================================
pause
