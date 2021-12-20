# Install nuitka
pip --quiet install nuitka

# Build Windows executable
New-Item -Force -Name build -ItemType directory | Out-Null
cd src/
$appVersion = python -c "from ztraining2strigo import VERSION; print(VERSION, end='')"
python -m nuitka `
    --onefile --windows-onefile-tempdir `
    --assume-yes-for-downloads `
    --windows-company-name=zenika --windows-product-name=ztraining2strigo `
    --windows-file-version=$appVersion --windows-product-version=$appVersion `
    --output-dir=../build `
    ztraining2strigo/
cd ..
New-Item -Force -Name dist/ -ItemType directory | Out-Null
Move-Item -Force -Path build/ztraining2strigo.exe -Destination dist/ztraining2strigo-$appVersion.exe
