import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import './HomePage.scss';

class HomePage extends Component {
    render() {
        return (
            <div onClick={() => this.props.toyAction(12)}>{this.props.count} ::: {`asd`}</div>
        );
    }
}

export const toyAction = (input) => (dispatch) => {
    dispatch({ type: "INC" });
};

const mapStateToProps = (state) => ({
    count: state.count,
});

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({toyAction}, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(HomePage);
