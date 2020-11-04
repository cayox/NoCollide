# How to Setup

1. Install Raspberry Pi Os onto the Raspberry Pi. Instructions can be found [here](https://www.raspberrypi.org/documentation/installation/installing-images/)

##### Once in the OS do the following:

2. Install python 3.8.5 This can be done by running the [included shell script](./install_python3-8-5.sh) by running the following commands in the terminal: 
    ```bash
    cd setup
    # make the shell script executable
    chmod +x install_python3-8-5.sh
    # run the script (This takes about 10 mins)
    sudo ./install_python3-8-5.sh
    ```

3. Install necessary Libraries:
    ```bash
    # from the setup directory
    pip install -r requirements.txt
    ```

4. connect the LiDAR (additional Info can be found [here](../docs/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf))

    |   Pin     |   Cable color     |
    |-----------|-------------------|
    |   2       |       Red         |
    |   3       |       Blue        |
    |   5       |       Green       |
    |   6       |       Black       |

    The remaining Cables must not be connected

5. Run the main script
    ```bash
    # from repository root
    cd src
    python3.8 main.py
    ```
