# BP: TODO List in 2024 H1

We have to make skyline more easier for development

## 1. Use sync mode instead of async mode [Done]

FastAPI sync mode is much more easier for coding than async.

We made a mistake to choose async mode at the very begining.

Async has advantages in performance however sync also enough since skyline is a cloud control console, not ebay or Amazon.

Skyline API service is light enough for a quick refactor, which is a lucky thing.

## 2. Upgrade libs

Lots of basic libs need to be upgraded:

1. Base docker image
2. SqlAlchemy 1.x -> 2.x
3. Python 3.11+ compatibility
4. React component versions
5. etc...

## 3. Accelerate CI/CD

1. Building docker image
2. Development & debugging
3. OpenDev CICD

## 4. Adding examples to show howto adding non-OpenStack components

More use cases, more popular.

Some enterprise use customized Skyline with non-OpenStack components, we could give some demo & coding examples.
