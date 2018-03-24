import React, { Component } from 'react';
import upvote from './upvote.png';
import upvoted from './upvoted.png';

export default class Vote extends Component {
  upvote_question() {
    fetch('/api/questions/' + this.props.id, {
      method: 'POST',
      credentials: 'include'
    });
    this.props.upvote_handler(this.props.id);
  }

  render() {
    var upvote_link;
    if (this.props.upvoted) {
      upvote_link = <img src={upvoted} alt="Vote" title="Vote" />;
    }
    else {
      upvote_link = (
        <a href="" onClick={this.upvote_question.bind(this)}>
          <img src={upvote} alt="Vote" title="Vote" />
        </a>
      );
    }
    return <span>{upvote_link}<span className="votes">{this.props.votes}</span></span>;
  }
}
