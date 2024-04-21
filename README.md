# MyCurrency

MyCurrency is a web platform designed to provide users with the ability to calculate currency exchange rates effortlessly. Leveraging an external provider, Fixer.io, MyCurrency retrieves and stores daily currency rates, ensuring accurate and up-to-date information for users. yet, MyCurrency is not limited to Fixer.io alone; it is built to seamlessly integrate with multiple currency data providers, accommodating any provider with different APIs for retrieving currency exchange rates.

With support for EUR, CHF, USD, and GBP as available currencies, MyCurrency offers flexibility and convenience for users to perform currency conversions efficiently. Whether for personal finance management, international transactions, or travel planning, MyCurrency simplifies the process of currency exchange rate calculation, providing users with a reliable and versatile platform.


## Table of Contents

- [Installation](#installation)
- [Technologies](#Technologies)
- [Endpoints](#Endpoints)
- [Drivers](#Drivers)
- [Adapters](#Adapters)
- [Back Office](#Back-Office)
- [Redis Caching](#Redis-Caching)
- [API Versioning](#API-Versioning)
- [Unit Tests](#Unit-Tests)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install and run this project, follow these steps:

1. **Clone the Repository:**
2. **Install Docker and Docker Compose:**
- Follow the official Docker documentation to install Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Follow the official Docker Compose documentation to install Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **Rename the Environment File:**
- Locate the `.env.example` file in the project root directory.
- Rename it to `.env`:
  ```
  mv .env.example .env
  ```

4. **Add FIXER_ACCESS_KEY in the .env File:**
- Open the `.env` file in a text editor.
- Find the variable `FIXER_ACCESS_KEY` and assign your Fixer access key to it:
  ```
  FIXER_ACCESS_KEY=your_access_key_here
  ```
- Save and close the file.

5. **Build and run docker compose:**
- Run these commands:
  ```
  docker-compose build
  docker-compose up
  ```

## Technologies
This project utilizes the following technologies:

- **PostgreSQL as Database:**
  PostgreSQL is a powerful, open-source relational database management system. It is well-suited for Django projects due to its support for complex queries, ACID compliance, and scalability, making it an excellent choice for storing structured data in this Django REST Framework project.

- **Pre-commit:**
  Pre-commit is a tool for managing and maintaining multi-language pre-commit hooks. It ensures that all code pushed to the repository passes through a series of automated checks before being committed. Utilizing pre-commit in this project helps maintain code quality, consistency, and adherence to best practices across the codebase.

- **Coverage:**
  Coverage is a tool for measuring code coverage during test execution. It helps identify areas of the codebase that are not adequately covered by tests. Integrating coverage into this Django REST Framework project ensures comprehensive test coverage, which is essential for maintaining code quality, identifying bugs, and reducing the risk of regressions.

- **corsheaders:**
  corsheaders is a Django application for handling Cross-Origin Resource Sharing (CORS) headers. It allows the server to specify who can access its resources, which is particularly important in this project when interacting with the API from different domains or origins.

- **Docker:**
  Docker is a containerization platform that simplifies the process of packaging, distributing, and running applications. Using Docker in this project ensures consistency across different environments, facilitates dependency management, and streamlines deployment workflows.

- **Docker Compose:**
  Docker Compose is a tool for defining and running multi-container Docker applications. It allows you to define the services, networks, and volumes required for your application in a single file. Utilizing Docker Compose in this project simplifies the management of containers, orchestrates the deployment of interconnected services, and promotes scalability and reproducibility.

- **Redis as Caching:**
  Redis is an open-source, in-memory data structure store that can be used as a caching layer. It provides high-performance caching capabilities, reducing the response time and load on the primary database server. Integrating Redis as a caching mechanism in this Django REST Framework project improves the overall performance and scalability of the application, especially for frequently accessed data.

## Endpoints

The API exposes the following endpoints:

1. **Providers Endpoint (`providers/`):**
   - **GET:** Retrieve the list of providers.
     Usage: Send a GET request to `/api/v1/providers/`.

   - **POST:** Create a new provider.
     Usage: Send a POST request to `/api/v1/providers/` with the following request body:
     ```json
     {
       "name": "<provider_name>",
       "api_url": "<api_url>",
       "endpoints": "<endpoints>",
       "priority": "<priority>"
     }
     ```
     **Note:** When specifying the endpoints parameter, include a dict of endpoints required for your provider. At least three endpoints are necessary: converter, historical, and symbols. While these names are default and can be easily changed in the .env file, your provider may not necessarily use the exact same names for these methods. In the endpoints list, define the endpoint names and query parameter names used by your provider. For instance, if your provider's converter endpoint is /convert_money/ and requires only two parameters, define it in the endpoints list as {'converter' : ['convert_money', 'parameter_one', 'parameter_two']}.

   - **PUT:** Prioritize a provider.
     Usage: Send a PUT request to `/api/v1/providers/` with the following request body:
     ```json
     {
       "name": "<provider_name>",
       "priority": "<priority>"
     }
     ```

   - **DELETE:** Delete a provider.
     Usage: Send a DELETE request to `/api/v1/providers/` with the following request body:
     ```json
     {
       "name": "<provider_name>"
     }
     ```

2. **Rates Endpoint (`rates/`):**
   - **GET:** Retrieve a list of currency rates for a specific time period.
     Usage: Send a GET request to `/api/v1/rates/` with query parameters:
     ```
     source_currency=<source_currency>&date_from=<date_from>&date_to=<date_to>
     ```
     Example: `http://127.0.0.1:8000/api/v1/rates/?source_currency=EUR&date_from=2024-01-01&date_to=2024-01-04`

3. **Convert Endpoint (`convert/`):**
   - **GET:** Calculate the latest amount in a currency exchanged into a different currency (currency converter).
     Usage: Send a GET request to `/api/v1/convert/` with query parameters:
     ```
     source_currency=<source_currency>&amount=<amount>&exchanged_currency=<exchanged_currency>
     ```
     Example: `http://127.0.0.1:8000/api/v1/convert/?source_currency=EUR&amount=10.0&exchanged_currency=USD`

4. **TWRR Endpoint (`twrr/`):**
   - **GET:** Retrieve time-weighted rate of return for any given amount invested from a currency into another one from a given date until today.
     Usage: Send a GET request to `/api/v1/twrr/` with query parameters:
     ```
     source_currency=<source_currency>&amount=<amount>&exchanged_currency=<exchanged_currency>&start_date=<start_date>
     ```
     Example: `http://127.0.0.1:8000/api/v1/twrr/?source_currency=EUR&amount=20&exchanged_currency=USD&start_date=2024-04-17`

**Note:** If you are using a custom provider not supported by MyCurrency and need to send custom query parameters for rates, convert, and twrr, feel free to include any parameters you need. In case a custom provider is found, the adapter will ignore the main query parameters and use the parameters you add at the end. For example, if your provider requires an access key (in the case of Fixer.io, you don't need to send an access key as it is supported), you can simply add it at the end of the URL:
Example: `http://127.0.0.1:8000/api/v1/twrr/?source_currency=EUR&amount=20&exchanged_currency=USD&start_date=2024-04-17&access_key=my_access_key`

## Drivers
In this project, drivers are classes responsible for retrieving data from the providers. Within `drivers.py`, there exists a class called BaseDriver, which retrieves data from the providers' model. It obtains the `api_url` (the base URL where requests should be sent) and, using the `endpoints` variable, dynamically creates functions and links them to specific endpoints of the provider. When a method is invoked, the corresponding endpoint of the provider is called, and the return value of the provider's endpoint becomes the return value of the method.

For example, if we register the `converter` endpoint in the `endpoints` field like this:
```
"converter": ["convert", "access_key", "currency_from", "to", "amount"]
```
it means that when we call the `converter` method and pass parameters from this driver, it will call the provider's `convert` endpoint. It will pass `"access_key"`, `"currency_from"`, `"to"`, and `"amount"` parameters to the provider as query parameters and return the response from the provider.

Note that in the list `["convert", "access_key", "currency_from", "to", "amount"]`, the first element (in this case "convert") is the name of the endpoint, and the rest are parameters.

In cases where the endpoint name is a parameter, you can simply send `endpoint="<endpoint-name>"`, which will override the first element of the list.

Additionally, there is a MockDriver for testing purposes. It mocks necessary methods and returns randomly generated data similar to real provider data.

## Adapters

In this project, Adapters ensure that every request for data retrieval is sent to every provider, and ensures that data received from each provider is returned in the same format. Within adapters.py, there exists a class called Adapter, which handles requests for all providers. It takes the list of active providers, sorts them by priority, and sends the request to each provider until it receives the data. If none of the providers are able to retrieve the data, it raises an error. The priority of a provider can be set to 0 (for example, in the case of a MockDriver) using the providers endpoint, and it will be ignored by the adapter.

## Back Office

The Exchange Rate Evolution Back Office/Admin is a crucial component of the project, offering administrative functionalities for managing and visualizing currency exchange-related data. The back office is implemented as a small site, leveraging Django admin for ease of development and administration.

### Functionalities

1. **Converter View:**
   The back office provides an online version of the Currency Converter, allowing users to set a source currency and multiple target currencies for conversion. This functionality is accessible via the following endpoint:
   - Endpoint: `/back_office/converter/`

2. **Graph View:**
   In addition to the Converter View, the back office offers a Graph View that visually displays the exchange rate time evolution comparison between different currencies. This graphical representation helps users analyze and understand the fluctuations in exchange rates over time.
   - Endpoint: `/back_office/graph/`

These functionalities empower users to efficiently manage currency conversion tasks and gain insights into exchange rate trends through intuitive graphical representations.

## Redis Caching

Redis caching plays a pivotal role in optimizing the performance and efficiency of the exchange rate retrieval process within the project. By implementing a batch procedure to retrieve exchange rates and caching/storing them, unnecessary calls to the exchange rate provider are avoided, thereby enhancing the overall responsiveness of the API.

### Batch Procedure for Exchange Rate Retrieval

A batch procedure has been designed to implement exchange rate caching and storing, ensuring efficient data retrieval without relying on the exchange rate provider for historical data requests. This procedure operates as follows:

1. **Data Retrieval from CSV or JSON:**
   The procedure fetches exchange rate data from a CSV or JSON file. This file contains the necessary historical exchange rate information required for caching/storing.

2. **Parsing and Storage:**
   Upon retrieval, the exchange rate data is parsed and stored into the appropriate models within the project. This ensures that the data is organized and readily accessible for future use.

### Implementation Details

The caching and storing process is facilitated through management commands within the project. Specifically, an `import_cache` command has been created to execute the batch procedure. This command is configured to run automatically each time the Docker Compose orchestrates the web container. It moves data from a default cache file, `default_cache.json`, to the cache storage.

## API Versioning

API versioning is a critical aspect of maintaining compatibility and managing changes in the MyCurrency API. To accommodate potential variations in API versions or scopes, URL path versioning has been implemented.

### URL Path Versioning

URL path versioning is employed to distinguish between different versions or scopes of the API. Each version of the API is represented in the URL path, allowing for clear differentiation and seamless transition between versions.

For example, this project is using the following URL structure:

- `http://example.com/api/v1/...`: Represents version 1 of the API.
- `http://example.com/api/v2/...`: Represents version 2 of the API.

By including the version number in the URL path, clients can explicitly specify which version of the API they wish to interact with. This approach enables developers to introduce new features, enhancements, or changes while ensuring backward compatibility and minimizing disruption for existing users.

**Note:** Only version 1 is implemented at this moment.

## Unit Tests

The project includes a comprehensive suite of unit tests to ensure the reliability and functionality of its components. The unit tests are organized within the `tests.py` file and cover various aspects of the API endpoints and functionality.

### Test Coverage

The unit tests provide extensive coverage of the project's functionalities, with a test coverage of 94%. This high level of coverage ensures that critical components are thoroughly tested and validated.

### Test Cases

#### ProvidersAPITest

1. **test_list_providers:** Tests the functionality to retrieve the list of providers.
2. **test_add_provider:** Tests the ability to add a new provider.
3. **test_prioritize_provider:** Tests the functionality to prioritize a provider.
4. **test_delete_provider:** Tests the functionality to delete a provider.

#### RatesAPITest

1. **test_get_rates:** Tests the functionality to retrieve exchange rates for a specific time period.

#### ConverterAPITest

1. **test_convert_currency:** Tests the functionality to convert currency.

#### TWRRAPITest

1. **test_get_twrr_values:** Tests the functionality to retrieve time-weighted rate of return values.

These test cases validate the correctness and reliability of key functionalities within the project, ensuring that they function as intended and provide expected results.



## Contributing

Thank you for considering contributing to this project! Whether you're reporting a bug, suggesting a feature, or submitting a pull request, your contributions are highly appreciated.

### Bug Reports

If you encounter a bug in the project, please open a new issue on GitHub. In your issue report, be sure to include detailed steps to reproduce the bug and any relevant information about your environment.

### Feature Requests

If you have an idea for a new feature or enhancement, please open a new issue on GitHub. Provide a clear description of the feature and explain why it would be valuable to the project.

### Pull Requests

We welcome pull requests from the community! Before submitting a pull request, please ensure that your code adheres to the project's coding conventions and standards. Also, make sure to write clear commit messages and provide a detailed description of the changes introduced by your pull request.

To submit a pull request:

1. Fork the repository and create your branch from `main`.
2. Make your changes and ensure that all tests pass.
3. Submit a pull request to the `main` branch of the main repository.

### Code Style

Please follow the existing code style and conventions used in the project. Consistent code style makes the codebase easier to maintain and understand for everyone.

### Contact

If you have any questions or need further assistance, feel free to contact the project maintainers.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
