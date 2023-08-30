@PUSHD %~dp0
@SET SPHINXOPTS=-W
@SET SPHINXBUILD=python -m sphinx
@SET SPHINXPROJ=battery_system_designer
@SET SOURCEDIR=.


@FOR /F "tokens=* USEBACKQ" %%F IN (`git rev-parse --show-toplevel`) DO @(
    @SET REPO_ROOT=%%F
)
@SET BUILDDIR=%REPO_ROOT%\build\doc

@IF not exist %BUILDDIR% @mkdir %BUILDDIR%

@IF "%1" == "" @(
    %SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
    @EXIT /B 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

@POPD
