``elabackup``
=============

*Quick and dirty CLI app to backup an eLabFTW instance using the HTTP API*


Installation
------------

Install with ``pip`` using the latest development version::

    $ pip install --user https://github.com/althonos/elabackup/archive/master.zip



Usage
-----

Running `elabackup --help` should give you the following message, if
you installed it successfully::

    elabackup - save / load backups of eLabFTW data using the API.

    Usage:
        elabackup dump -a <apikey> -s <server> [-o <output>] [--traceback]
        elabackup load -a <apikey> -s <server>  -i <input>   [--traceback]

    Parameters:
        -a <apikey>, --apikey <apikey>  The eLabFTW OAuth token to use.
        -s <server>, --server <server>  The adress of the server.

    Parameters - Dump:
        -o <output>, --output <output>  The name of the output file. Defaults
                                        to `elab-backup-<date>.json.gz`.

    Parameters - Load:
        -i <input>, --input <input>     The name of the input file.

    Parameters - Debug:
        --traceback                     Show full traceback on error.


Go to the


Example
-------

.. code:: console

     $ elabackup dump -a $ELAB_TOKEN -s https://elab.inbio.pasteur.fr:3148/
     $ ls
     elab-backup-2018-08-17.json.gz
