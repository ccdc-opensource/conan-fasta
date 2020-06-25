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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "fasta36-fasta-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_msvc(self):
        with tools.vcvars(self.settings):
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                self.run("nmake /f ../make/Makefile.nm_pcom all")

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
            self._build_msvc()
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
        self.copy("COPYRIGHT", src="sources", dst="licenses")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
