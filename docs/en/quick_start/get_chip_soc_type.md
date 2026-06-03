# Method for Obtaining the SoC Model of Ascend Chips

<br>

>[!NOTE] Note  
>**Basics About Ascend Chip SoC Models (Important)**  
>Ascend A2/A3 represent product generations:  
>A2: AI acceleration platform based on Atlas A2 training products/Atlas A2 inference products.  
>A3: AI acceleration platform based on Atlas A3 training products/Atlas A3 inference products.  
>Different chip models have hardware differences, and upper-layer tools can perform differentiated processing based on the "chip SoC model" (for example, Ascend910B4).

## 1. Obtaining NPU ID and Chip ID

Execute the following command:

```shell
npu-smi info -m
```

Example output:

```text
[root@localhost ~]$ npu-smi info -m
        NPU ID                         Chip ID                        Chip Logic ID                  Chip Name                     
        0                              0                              0                              Ascend 910B4
        0                              1                              -                              Mcu                           
        1                              0                              1                              Ascend 910B4
        1                              1                              -                              Mcu         
```

It is generally assumed that all chip types on a server are the same, so you can use the NPU ID and chip ID values from the first row of data (or you can use your specified values). For example, in the output above, the NPU ID is 0 and the chip ID is 0.

## 2. Obtaining the Chip Name Based on the IDs

Run the following command, where the value of -i is the NPU ID obtained above, and the value of -c is the Chip ID obtained above:

```shell
npu-smi info -t board -i 0 -c 0
```

Example output for an A2 environment:

```text
[root@localhost ~]$ npu-smi info -t board -i 0 -c 0
        NPU ID                         : 0
        Chip ID                        : 0
        Chip Type                      : Ascend
        Chip Name                      : 910B4
```

Example output for the A3 environment is as follows:

```text
[root@localhost ~]$ npu-smi info -t board -i 0 -c 0
        NPU ID                         : 0
        NPU Name                       : 9392
        Chip ID                        : 0
        Chip Name                      : Ascend910
```

For A2/A3 chips: Both A2 and A3 chips have a **Chip Name**; A3 has an **NPU Name**, while A2 does not; A2 has a **Chip Type**, while A3 does not.

## 3. Concatenating the Final Chip SoC Model

The SoC model format for A2 chips is: `{Chip Type}{Chip Name}`, for example: Ascend910B4.   
The SoC model format for A3 chips is: `{Chip Name}_{NPU Name}`, for example: Ascend910_9392.

After obtaining the chip SoC model using the formulas above, please record it, as it will be needed in subsequent steps.
