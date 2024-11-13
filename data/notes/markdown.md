# Markdown Syntax
## Code Documentation  
- The syntax below uses triple backticks followed by the code language
- Placing the entire code + outputs in a markdown block `>` enhances readability
> ```python
> # To print hello world in python
> print("Hello World!")
> ```
> Hello World!
 

> ```shell
> # To see the current CPU architecture in linux
> dpkg --print-architecture  
> ```
> arm64

> ```shell
> # To get information about the current linux OS
> cat /etc/os-release  
> ```
> PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"  
> NAME="Debian GNU/Linux"  
> VERSION_ID="11"  
> VERSION="11 (bullseye)"  
> VERSION_CODENAME=bullseye  
> ID=debian  

> ```shell
> # To see the current linux kernel
> uname -r  
> ```
> 6.1.43-rockchip-rk3588  

## Alerts

> [!NOTE] 
> Useful information that users should know, even when skimming content.  

> [!TIP] 
> Helpful advice for doing things better or more easily.  

> [!IMPORTANT] 
> Key information users need to know to achieve their goal.  

> [!WARNING] 
> Urgent info that needs immediate user attention to avoid problems.  

> [!CAUTION] 
> Advises about risks or negative outcomes of certain actions.  
