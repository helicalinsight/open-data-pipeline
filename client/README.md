### Technologies used

- React
- Redux + redux-thunk
- antd
- Jest + react-testing-library

### Setup / Installation:

- Clone the Repo. open console/terminal inside your project directory.
- Goto client directory inside the ML project. Run cd `./client`.
- Run `npm install` for first time to install the dependencies in your local machine.

## Start project in development mode `npm start`

To start application in local

1. Remove `homepage` in `package.json` file
2. In `paths.js` file replace `sparkBuildPath` with `localBuildPath` in `appBuild` key
3. Comment this `filename: "../../templates/index.html"` in `webpack.config.js`

please do not push the above changes to git

4Starts the project in your local machine at port 3000. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Create a build of react app `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

## To run the test cases `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

If your app uses a browser API that you need to mock in your tests or if you need a global setup before running your tests, add a `src/setupTests.js` to your project. It will be automatically executed before running your tests.
