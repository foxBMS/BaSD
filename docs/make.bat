@PUSHD %~dp0
@SET SPHINXOPTS=-W
@SET SPHINXBUILD=python -m sphinx
@SET SPHINXPROJ=battery_system_designer
@SET SOURCEDIR=%~dp0
@SET BUILDDIR=%~dp0..\build\doc

@IF not exist %BUILDDIR% @mkdir %BUILDDIR%

@IF "%1" == "" @(
    %SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
    @EXIT /B 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

@POPD
