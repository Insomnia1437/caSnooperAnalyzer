# caSnooperAnalyzer

> [caSnooper User Guide](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html)

| option    | explanation                                                  |
| --------- | ------------------------------------------------------------ |
| -c<int>   | Check validity of top n requests (0 means all). That is, try to connect to these process variables. Timeout after 10 s. See [Report](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#Report). |
| -d<int>   | Set debug level to n. Prints extra information for debugging. |
| -h        | Help.                                                        |
| -i<str>   | Specify a PV name to watch individually. The default is CaSnoop.test. (The default is not affected by setting the prefix with -n.) See [Individual Process Variable Name](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#IndividualPVName). |
| -l<dec>   | Print all requests over n Hz. See [Report](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#Report). |
| -p<int>   | Print top n (0 means all). See [Report](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#Report). |
| -n[<str>] | Make internal PV names available. Use string as prefix for internal PV names (10 chars max length). Default string is: CaSnoop. See [CaSnooper Process Variables](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#ProcessVariables). |
| -s<int>   | Print all requests over n sigma. See [Report](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/CaSnooper/CaSnooper.html#Report). |
| -t<dec>   | Run n seconds, then print report.                            |
| -w<dec>   | Wait n sec before collecting data. Use to wait until searches resulting from CaSnooper's coming up are over. |

