import React, { Component } from 'react';
import './App.css';
import Question from './Question.js';
import reload from './reload.png';

export default class App extends Component {
  state = {
    questions: [],
  };

  upvote_question(id) {
    var new_questions = this.state.questions;
    for (var i = 0; i < new_questions.length; i++) {
      if (new_questions[i].id === id) {
        new_questions[i].votes += 1;
        new_questions[i].upvoted = true;
      }
    }
    this.setState({questions: new_questions});
  };

  reload_questions() {
    this.state.questions = [];
    this.update_questions();
  }

  componentDidMount() {
    this.update_questions();
    setInterval(this.update_questions.bind(this), 5000);
  }

  update_questions() {
    this.callApi()
      .then(res => {
        var new_questions = this.state.questions;
        for (var i = 0; i < res.length; i++) {
          var q = res[i];
          for (var j = 0; j < new_questions.length; j++) {
            if (new_questions[j].id === q.id) {
              new_questions[j] = q;
              break;
            }
          }
          if (j >= new_questions.length) {
            new_questions.push(q);
          }
        }
        this.setState({ questions: new_questions });
      })
      .catch(err => console.log(err));
  }

  callApi = async () => {
    const response = await fetch('/api/questions', { credentials: 'include' });
    const body = await response.json();

    if (response.status !== 200) throw Error(body.message);

    return body;
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Flask Webcast</h1>
          <h3>Q&A</h3>
        </header>
        <ul className="App-body">
          <a href="#" onClick={this.reload_questions.bind(this)}>
            <img src={reload} title="Reload" alt="Reload" />
          </a>
          {this.state.questions.map(function(q) {
            return <Question key={'question' + q.id} question={q} upvote_handler={this.upvote_question.bind(this)} />;
          }, this)}
        </ul>
      </div>
    );
  }
}
