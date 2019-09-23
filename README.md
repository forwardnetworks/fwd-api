
Being able to programmatically upload checks and aliases is
important. It can simplify setting up deployments of similar
topologies across different networks (e.g., in a plugfest with
multiple vendors), allow quickly and easily sharing configurations
(e.g., for demos), and simplify other testing. This repository
contains python libraries and scripts to automate uploading aliases
and checks.

Install
-----------------

You can either scope the installation of the ```fwd_api``` python
module to a virtual environment or install it system-wide. The first
is recommended.

### Installing in a virtual env
Get virtualenv

   pip install virtualenv

From the ```fwd-api``` directory, create a virtual environment for
Python:

   virtualenv fwd_virtual

This should produce a folder named ```fwd_virtual```. Use the virtual
environment by calling:

   source fwd_virtual/bin/activate

From this same terminal, follow the instructions in the system-wide
instructions.

### Installing system-wide
fwd-api depends on python's request module. To get it, use pip:

   pip install requests

After installing requests, use ```setup.py``` to install the fwd_api
module; from the fwd-api directory, run:

   python setup.py install
