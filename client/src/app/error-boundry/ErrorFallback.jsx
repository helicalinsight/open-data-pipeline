import isEqual from "lodash.isequal";
import { connect } from "react-redux";
import React from "react";

class ErrorFallback extends React.Component {
  state = {
    error: false,
  };
  componentDidCatch(error, info) {
    if (error) {
      this.setState({ error: error });
    }
  }
  componentDidUpdate(prevProps) {
    if (this.state.error && !isEqual(prevProps, this.props)) {
      this.setState({ error: false });
    }
  }
  render() {
    return <>{this.props.children}</>;
  }
}

export default connect(null, null)(ErrorFallback);
