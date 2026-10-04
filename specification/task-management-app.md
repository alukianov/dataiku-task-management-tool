# Task Management Application — Technical Test Specification

## Instance URL

[https://luk-ole.rnd1.candidates.ondku.net/](https://luk-ole.rnd1.candidates.ondku.net/)

## Context

You are asked to test a task management application. The application is composed of two parts:

1. A RESTful API
2. A single-page web application

Users can add, delete and edit a task. A task has the following attributes:

- A title (maximum length 20)
- A status
- Its creation time
- Its owner
- Optionally, a list of tags. Non-existing tags are created automatically when the task is created. The name of a tag cannot exceed 20 characters.

## Authentication

Some actions require authentication to be performed. Two ways of authentication are provided:

1. Simple user/password HTTP authentication
2. Token authentication (see the `/authenticate` endpoint). In this case, the token is given as a username and the password can be any value. Tokens expire after 10 minutes.

A test user is already created with the following credentials:

- username: `QA`
- password: `willWin`

## Database reset

In order to make test reproducibility easier, a `/reset` action is provided to drop all existing data and re-create the default user. Note that this action does not have to be tested.

## RESTful API

The base URL for the REST API is `<service_host>:<service_port>`. The different endpoints are described in the table below.

| URL | Method | Expected data | Result | Needs authentication |
|---|---|---|---|---|
| `/` | GET | N/A | The list of existing tasks | No |
| `/` | PUT | `{ "title": <string>, "tags": <array of string> }` | The created task | Yes |
| `/<task_id>` | GET | N/A | The description of the task | No |
| `/<task_id>` | DELETE | N/A | N/A | Yes, and owner of the task |
| `/<task_id>` | PATCH | `{ "title": <string>, "tags": <array of string>, "done": <boolean> }` | The updated task | Yes, and owner of the task |
| `/tags` | GET | N/A | The list of existing tags | No |
| `/tags/<tag_id>` | GET | N/A | The description of the tag | No |
| `/users` | POST | `{ "username": <string>, "password": <string> }` | The created user | No |
| `/authenticate` | POST | `{ "username": <string>, "password": <string> }` | The generated token | N/A |
| `/reset` | GET | N/A | N/A | No |

## Single-page web application

Some actions (add, edit, mark as done, delete) are exposed through a single-page web application. This application can be accessed at the following URL:

`<service_host>:<service_port>/web/index.html`

## What is expected

Three things are expected:

1. Automated backend tests
2. Automated frontend tests
3. Bug reports for problems found

For the tests:

- Automated tests are highly recommended; nevertheless, part of the test suite may consist of manual tests.
- No specific tool is required, but the tests should rely on free and publicly-available tools only, and all instructions to re-run them must be provided.
- They should be in a private GitHub repository, made accessible to the people who interviewed you (their GitHub handles should be in the email received, but ask for them if they are not).

The bugs can be reported using the tool and format preferred.

A particular attention will be given to the quality of the code as much as the relevance of the bugs found. A list of improvements thought about but not implemented can also be provided.

There is one week to complete the technical test, with more time available if needed, provided it is communicated in advance. It is not necessary to test everything and find all bugs — use judgment to show what matters most. In general, an enterprise-level project (i.e. showing how you work) is expected, rather than a showcase of fancy technologies.
