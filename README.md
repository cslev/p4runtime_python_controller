# p4runtime_python_controller
This repository containes a simple P4Runtime controller written in python to be used as a skeleton

# Environment
The python libraries were slightly modified (compared to the 'plain-old' p4lang/tutorial examples) to match other necessary  libraries's (grpc,protobuf,PI) needs.

## Docker container environment for usage
In order to have the eligible environment to run this controller application, obtain the following docker image from the Dockerhub:
[https://hub.docker.com/r/cslev/p4controller/](https://hub.docker.com/r/cslev/p4controller/)

The image itself is based on `ubuntu:18.04` (instead of `ubuntu:16.04`), which has quite fresher libraries. It means that, for instance, the *grpc* (required for communicating with the switch) has been slightly changed/upgraded and some of the core python modules have been separated.
See the head of `p4runtime_lib/switch.py`, where, besides `p4runtime_pb2.py`, the switch needs `p4runtime_pb2_grpc.py` as well for the connection, where the latter is used in the constructor (only).

## Other adjustments compared to p4lang/tutorial example
 - paths to python libraries in the head of the python source files in p4runtime_libs (`v1/` added to the paths)
 - `helper.py` was looking for `convert.py` in a subdirectory, but they are in the same
 
# What this repository IS NOT ABOUT
 - how to create and install your p4runtime environment (it is based on ubuntu:18.04 and installation instructions of plang/PI should be followed)
   - However, you do not need to do this! Just obtain the docker image I have provided above!
 - how the switch behaves (really simple, check source code) as described in the .p4 file (compiled .json file with p4runtime info file .p4info are also there)
