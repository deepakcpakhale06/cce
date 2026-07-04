Target - I want to build an app which allows non-technical users to do a cost estimation for their AWS setup.

Features

1. Application should be containerized as a docker container.
2. Application should be browser based with easy to navigate UI
3. Application does not need any persistent storage, however it should allow user to export the cost in an editable excel file.
4. When the app is opened in the browser, User should see a section where he can describe his target setup.
5. Cost estimator app should be able to analyze the target system/setup description provided by the user. This can be done using LLM integration. App Should have a place for user to do required integrations with LLM models. It should support anthropic, openai, gemini, Grok or even locally hosted models.
6. After App is done with user input Analysis, it should generate rows with following columns(Column Name and Description are mentioned below)
    1. Column-1
        1. Name - Component/Function Name
        2. Depending on the user description, identify the component name. User can always change this.
    2. Column-2
        1. Name - AWS Service Name
        2. Select Suitable AWS Service to host the component. User can always change this
        3. Make this a dropdown list
    3. Column-3
        1. Name - Quantity
        2. Required number of instances of the AWS Service
    4. Column-4
        1. Name - Configuration
        2. This should match with the AWS Pricing calculator fields available for the Service
        3. This Column can be a free text with some default choices already done for the user
        4. User can always change the values, however user should know which fields are absolutely mandatory and which ones are optional
    5. Column-5
        1. Name - Assumptions
    6. Column-6
        1. Name - Cost Per Month(USD)
        2. This price is calculated, depending on the latest pricing available for the service in the selected region
    7. Column-7
        1. Name - Yearly Cost(USD)
        2. This price is calculated, depending on the latest pricing available for the service in the selected region
7. React is used for frontend and backend is using latest python version
8. On the UI user should have a place to select AWS region from the dropdown and regional pricing should be used for estimation.
9. Use the bulk API for https://pilotcore.io/blog/how-to-use-aws-price-list-api-examples#aws-price-list-bulk-api to query the cost. Make sure the API calls are done in a most efficient and optimum manner without causing too much CPU and memory overhead.