## To get started:

Optionally set up and activate virtual env, install required dependencies and run `main.py`:

```console
$ git clone git@github.com:cowboy-bebug/zerohash-py.git
$ cd zerohash-py
$ python3 -m venv ./venv                 # optionally create venv
$ source ./venv/bin/activate             # optionally activate venv
$ pip install -r requirements.txt        # installs dependencies for production
$ pip install -r requirements-local.txt  # installs local dev dependencies
$ python main.py                         # run the main script
```

To run tests:

```console
$ pytest --verbose
```

To run formatter:

```console
$ black .
```

To run linter (max line length is coming from `black`):

```console
$ flake8 --exclude=venv --max-line-length=88
```

## Design Considerations

My design choice above all else is in minimalism. I am a very big fan of talks such as [Small Is Beautiful](https://www.youtube.com/watch?v=B3b4tremI5o), where writing smaller pieces of code could be considered more valuable in organizations. I have intentionally left out using `class`, for example, because there is not yet a need for it. In my opinion, OOP principles or design patterns become much more valuable when they are introduced at a later stage, where the codebase in question is mature enough as features and access patterns are more ironed out.

I initially considered using `queue` and ended up with the `deque` data structure as I wanted a circular buffer with fixed capacity of 200 elements and `deque` is optimized for that use case (eg, appending and popping from both ends are `O(1)` for `deque` compared to `O(n)` in `list`). Computing the length of `deque` is also `O(1)`, which makes the overall VWAP pretty efficient.

## Assumptions

My biggest assumption is relying on the `coinbase` websocket connection to be healthy. I have not encountered any errors yet so `on_error()` just logs out any errors received. Also, retry mechanism isn't properly implemented because of this. I think simple reconnection may suffice inside `on_close` (but I'd like to observe this behavior in real life to make sure). If not, we could wrap in `multiprocessing.Process` and manually restart processes if terminated.

Another assumption is that we will never run into message flooding issues. I have not yet observed any memory leak and I'm quite confident that it can handle the load. If we run into this problem in future, we can put a queuing layer in front to buffer some of the spikes.
