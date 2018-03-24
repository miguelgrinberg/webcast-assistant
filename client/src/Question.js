import React, { Component } from 'react';
import Vote from './Vote.js';

export default class Question extends Component {
  render() {
    return (
      <li>
        <Vote id={this.props.question.id} votes={this.props.question.votes} upvoted={this.props.question.upvoted} upvote_handler={this.props.upvote_handler} />
        <span dangerouslySetInnerHTML={{__html: this.props.question.question}} />
        <span className="author"> ({this.props.question.author})</span>
      </li>
    );
  }
}
