import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class FastaConan(ConanFile):
    name = "fasta"
    version = "36.3.8f"
    url = "https://github.com/wrpearson/fasta36"
    description = "FASTA36 sequence comparison software"
    license = "Apache-2.0"
    homepage = "https://fasta.bioch.virginia.edu"
    topics = ("conan", "protein", "sequencing")
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = 'sources'
    generators = "make"
    exports_sources = '*'
    
    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('7zip/19.00')

    def source(self):
        if self.settings.os_build == "Windows":
            archive_name='fasta-36.3.8e.7z'
            # Building on windows requires intel C compiler... I'll just grab a build
            tools.get(
                url=f'https://artifactory.ccdc.cam.ac.uk:443/artifactory/ccdc-3rdparty-windows-runtime-exes/{archive_name}',
                sha256=' 116e4ba09caf8ca1d3044dfec111655550e27ae70ddd1b8a75a7dd27df8ebb02',
                headers={
                'X-JFrog-Art-Api': os.environ.get("ARTIFACTORY_API_KEY", None)
            })
            self.run('7z x %s' % archive_name)
            os.unlink(archive_name)
            os.rename('fasta-36.3.8e', self._source_subfolder)
        else:
            tools.get(**self.conan_data["sources"][self.version])
            extracted_dir = "fasta36-fasta-v" + self.version
            os.rename(extracted_dir, self._source_subfolder)

    def _build_macos(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                self.run("make -j -f ../make/Makefile.os_x86_64 all")

    def _build_linux(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                self.run("make -j -f ../make/Makefile.linux64_sse2 all")

    def build(self):
        if self.settings.os_build == "Windows":
            pass # just grab the build
        elif self.settings.os_build == "Macos":
            self._build_macos()
        elif self.settings.os_build == "Linux":
            self._build_linux()

    def package(self):
        self.copy("*", src="sources/bin", dst="bin")
        self.copy("*", src="sources/conf", dst="conf")
        self.copy("*", src="sources/data", dst="data")
        self.copy("*", src="sources/misc", dst="misc")
        self.copy("*", src="sources/psisearch2", dst="psisearch2")
        self.copy("*", src="sources/scripts", dst="scripts")
        self.copy("*", src="sources/seq", dst="seq")
        self.copy("LICENSE", src="sources", dst="licenses")
        self.copy("COPYRIGHT", src="sources/", dst="licenses")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
