# TSP Camera Service

## Prerequisites
- Python and Vitual environment: see prerequisites of TSP project

## Active virtual environment
- For Ubuntu
    ```
    conda activate <<name_env>>
    ```
- For Windows 10/11:
    ```
    <<name_env>>\Scripts\activate
    ```
## Install necessary libraries for first time
    pip install -r requirements.txt
## Run TSP Camera Service project

- Checkout branch master
```
git checkout origin master
```
- Run
    - for Ubuntu

        ```
        set PYTHONPATH=$pwd
        python src\app.py
        ```
    - for Windows

        ```
        set PYTHONPATH=%cd%
        python src\app.py
        ```

- Call API from IP: localhost:8002
- Check list API (Swagger): localhost:8002/docs
