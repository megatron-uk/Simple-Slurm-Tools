### modulespy

The *modulespy* command recurses through the dependencies of a given Linux [module](https://modules.readthedocs.io/en/latest/), as would be instantiated via the normal '**module load packagename**' command.

Its purpose is to recursively find **all** child modules loaded by the named module. 

Module environments can get rather complex, and it is often difficult to understand the relationship between dependencies, this tool lets you know **exactly** which modules are loaded when you load a specific one.

#### Requirements

   * Python 3
   * Access to the '**module show**' command

#### Example

The command only takes a single option; the name of the module to query. An example showing all the dependencies of a GCC module is shown below:

        $ modulespy GCC
        modulespy - A loadable module interrogation tool
        ================================================
    
        Searching for all dependencies of: GCC
        GCC -> GCCcore/12.3.0
        GCC -> binutils/2.40-GCCcore-12.3.0
        binutils/2.40-GCCcore-12.3.0 -> GCCcore/12.3.0
        binutils/2.40-GCCcore-12.3.0 -> zlib/1.2.13-GCCcore-12.3.0
        zlib/1.2.13-GCCcore-12.3.0 -> GCCcore/12.3.0
    
        OK
        $