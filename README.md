# caSnooperAnalyzer

This project is for control people to check the load of the EPICS network.

Using caSnooper to analyze Channel Access broadcast packets every day and send the result to your email

## How to use
### checkout this program
`git clone https://github.com/Insomnia1437/caSnooperAnalyzer.git`

### configuration
1. modify the config file `config/config.ini`
2. modify the shell script `src/cron.sh`

### run this project as a crontab job

use `crontab -e` to edit your crontab job. Perhaps you need to set the `$EDITOR` env value first.

use your own python and your path. do not forget to execute `chmod 777 cron.sh` command.
 
`30 * * * * /home/sdcswd/workspace/python/caSnooperAnalyzer/src/cron.sh`

### Using ElasticSearch as a database

We (KEK Linac Control Group) began to use ElasticSearch and Logstash to monitor the Control Network environment recently.

But running two `caSnooper` might cause the `beacon anomaly`. See [https://epics.anl.gov/base/R3-14/12-docs/CAref.html#casw](https://epics.anl.gov/base/R3-14/12-docs/CAref.html#casw)

One of the solution is to use the data from ElasticSearch database.

Using this method, crontab should run every day:

`0 8 * * * /home/sdcswd/workspace/python/caSnooperAnalyzer/src/cron.sh`

The CaSnooper parse results in ES document:

```json
{
        "_index" : "linac-casnooper-2020.05.27",
        "_type" : "_doc",
        "_id" : "uCxbVnIBlwLZIrpPx2Zq",
        "_score" : 1.0,
        "_source" : {
          "@version" : "1",
          "@timestamp" : "2020-05-27T13:39:14.897Z",
          "pv" : "LIiRF:SECT36:MON_PHASE_PEAK1:QFE:10S",
          "Hz" : 0.2,
          "message" : "  79 lcbbc78.linac.kek.jp:57305     LIiRF:SECT36:MON_PHASE_PEAK1:QFE:10S 0.20",
          "host" : "lcbbc78.linac.kek.jp:57305"
        }
      }
```

**If you do not use ES, leave the elasticsearch configuration items blank in the `config.ini`.**

## caSnooper
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

