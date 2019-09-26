# code-challenge

## Setup instructions

* Install requirements
  ```shell
  $ pip install -r requirements.txt
  ```

* Initialize the DB
  ```shell
  $ ./cli.py init-db --make-dummy-data
  ```

* Try using the CLI

  ```shell  
  $ ./cli.py update-question-text 1 "Updated text"
  $ ./cli.py diff-question 1
  - Question 1 v3
  + Updated text
  $ ./cli.py diff-question 1 --version 2
  - Question 1 v2
  ?             ^
  
  + Question 1 v3
  ?             ^
  ```

* Try using the API
  ```shell
  $ FLASK_APP=web.py flask run
  ```
  In another terminal:
  ```shell
  $ curl localhost:5000/question/1 -XPUT -d 'Updated again!' -H 'Content-type: text/plain'
  $ curl localhost:5000/diff/1
  - Updated text
  + Updated again!
  $ curl localhost:5000/diff/1?version=2
  - Question 1 v2
  ?             ^
  
  + Question 1 v3
  ?             ^
  ```

## What went well

I tried out a new design I've been thinking about for a while on this project. Rather than going
whole-hog with a particular framework, I build the inner layers of the application using reusable
framework-agnostic components. This is half of the reason the SQLAlchemy session gets passed around
so much, and I think that the ease with which I could add features to both the CLI and API
demonstrated the potential advantages of this approach.<sup>1</sup>

The other half of the reason for the pervasive `session` argument is to make the code more testable.
Testing pure code is much easier than dealing with side-effects, so if the session isn't passed into
a function, you know you can test it purely without having to mock anything.<sup>2</sup> It's a bit hard to see
that paying off in the code as-is since the only piece of pure logic is the diffing, and that
basically just uses a stdlib module, but I suspect that as the project grew, pure business logic
would become a larger and larger proportion of the LoC. One can also imaging the session argument as
a placeholder for a collection of side-effects, sort of a general application context, that can be
built differently as-needed for different needs (testing, CLI, API, etc.)

## What was difficult

I lost some time chasing bugs that were hard to track down because they occurred in code involving
details of Flask, Click, or SQLAlchemy and produced truly massive and incomprehensible stack traces.
I suspect though that those were mostly growing pains, and that once this project matured a little
more those kinds of issues would become rarer.

## What I'd improve

I chose not to use mypy for this project because of time constraints, but doing so likely would've
caught some of the aforementioned bugs before they became errors. The code is structured in such a
way that it wouldn't be too hard to get it to typecheck cleanly either.

Error handling is more of a proof-of-concept than a full pattern. To productionalize this, I'd want
different errors representing different cases so the outermost layer could distinguish between
different cases and handle them appropriately. For now, the important distinction is that
`AppError`s are expected to occur during the course of normal operations (i.e. 400-class). Other
errors represent truly unexpected ("exceptional") cases (i.e. 500-class).

There's still plenty of cleanup work that I would've liked to do: repeated code, incomplete
patterns, etc. But the code works and fulfills the requirements, and I'd be hesitant to spend too
much time doing that cleanup now before we knew how the project would grow.

---

<sup>1</sup> I'm aware that Flask has CLI features built-in and that tools exist for easily making
CLIs out of APIs, this is intended as a demonstration of a design to solve a broader problem. What
if you wanted to shift some of the work to background workers? What if you wanted to change to
Falcon for performance?

<sup>2</sup> I would've liked to have demonstrated this by writing some tests, but I decided to use
the available time to flesh out the project functionality more instead.