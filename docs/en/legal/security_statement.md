# Security Statement

## System Security Hardening

It is recommended that users enable ASLR (Level 2), also known as **full random address space layout randomization**, in the system. This can be configured by referring to the following method:

```sh
echo 2 > /proc/sys/kernel/randomize_va_space
 ```

## Running User Recommendations

1. All tools in this code repository are designed for installation and use with low privileges. From the perspective of security and the principle of least privilege, none of the tools should be used with high-privilege accounts such as root. It is recommended to install and execute them with a standard user account.

2. If the tool depends on CANN, for security purposes, the CANN package installed by default with the same low-privilege user should be used. After executing source, do not arbitrarily modify the environment variables involved in set_env.sh.

3. Before using any tool in this repository, it is recommended to set umask to 0027 or higher to ensure that generated files meet the minimum permission security requirements.

## File Permission Control

1. When users provide input files to the tool, it is recommended that the file owner be consistent with the tool process owner, and that file permissions not be modifiable by others (including group and others). By default, the tool's on-disk file permissions are not writable by users in the same group or other users. Users can perform permission control on the generated files as needed.

2. Users need to properly control permissions during installation and usage. It is recommended to refer to the file permission reference for configuration.

## File Permission Control

| Type                               | Maximum Linux Permission Reference |
| ---------------------------------- | ------------------- |
| User home directory                         | 750 (rwxr-x---)   |
| Program files (including script files, library files, etc.)     | 550 (r-xr-x---)    |
| Program file directory                       | 550 (r-xr-x---)    |
| Configuration files                           | 640 (rw-r-----)    |
| Configuration file directory                       | 750 (rwxr-x---)    |
| Log files (recorded or archived)     | 440 (r--r-----)    |
| Log files (being recorded)                 | 640 (rw-r-----)    |
| Log file directory                       | 750 (rwxr-x---)    |
| Debug files                          | 640 (rw-r-----)    |
| Debug file directory                      | 750 (rwxr-x---)    |
| Temporary file directory                       | 750 (rwxr-x---)    |
| Maintenance and upgrade file directory                   | 770 (rwxrwx---)    |
| Business data files                      | 640 (rw-r-----)    |
| Business data file directory                   | 750 (rwxr-x---)    |
| Key components, private keys, certificates, ciphertext file directory | 700 (rwx------)    |
| Key components, private keys, certificates, encrypted ciphertext     | 600 (rw-------)    |
| Encryption/decryption interfaces, encryption/decryption scripts             | 500 (r-x------)    |

## Vulnerability Security Statement

For details, please refer to [MindStudio Vulnerability Mechanism Statement](./vulnerability_handling_procedure.md).

## Data Security

During tool usage, some code lines related to specific functions will access customer operator code. If the operator code is confidential and must not be disclosed, users should promptly delete the corresponding deliverables after use to prevent unnecessary information leakage.

## Build Security

This project supports source code compilation and installation. During compilation, dependent third-party libraries will be downloaded and build shell scripts will be executed. Temporary program files and compilation directories will be generated during the compilation process. Users can manage permissions on files within the source code directory as needed to reduce security risks. During the build process, users can modify build scripts as needed to avoid related security risks, and should pay attention to the security of build results.

## Runtime Security

1. When loading a dataset, if the memory size required for loading the dataset exceeds the memory capacity limit, it may cause errors and lead to unexpected process exit. If the collection time is too long, causing the generated data to exceed the remaining disk space, it may lead to abnormal exit.

2. When the tool exits the process and prints an error message upon an exception, this is normal behavior. It is recommended that users locate the specific cause of the error based on the error prompts, including by viewing log files and the result files generated during the collection and parsing process.

3. During tool usage, the tool does not perform security validation on user-input programs. Users must ensure the security of their programs themselves.

## Public Network Addresses

The tool does not involve the use of public IP addresses.

## Public Interfaces

This project is jointly developed using C++ and Python. All provided external interfaces have been disclosed in the documentation. The dynamic libraries do not directly provide services, and the exposed interfaces are for internal use. Users are not recommended to use them.

For scripting languages such as Python, the source code is released. It is recommended to directly use the public interfaces described in the documentation. Directly calling interface source code that is not explicitly disclosed is not recommended.

The interfaces exposed by the dynamic libraries compiled from msopcommon are for internal use. Users are not recommended to arbitrarily modify or use them.

## Instructions for Using Security Functions

Insecure functions are not forcibly disabled, but it is recommended to use the _s secure versions that explicitly pass the buffer length as a parameter, such as memset_s and memcpy_s.

## Communication Security Hardening

Remote communication is not involved at present. It is recommended that users use the tool in a secure network environment with a firewall or local area network, and pay attention to the communication security of other third-party software.

## Communication Matrix

External port communication is not involved at present.
