# Implementation resutls after every new functional improvements
This markdown file is created just to compare with the results before and after implementing
a new function to analyze whether there is an improvement or no improvement. Here I included only the top 3,
and the exact answer.

Outputs are eaxctly copied from the terminal.

## After implementation of the metadata aware finding the code snippets
After testing with the actual repository

**q1:** Where is HTTPAdapter.send implemented?

**Retreieved result:**
Vector results: 10
BM25 results: 10
Exact matches: 1
Fused results: 16

Eaxct match ranking: 7

Final rank: 7
Ranks: {'exact': 1}
Exact match: True
RRF score: 0.01639
Vector rank: —
BM25 rank: —
File: src/requests/adapters.py
Symbol: HTTPAdapter.send
Lines: 634-748

Code preview:
HTTPAdapter.send
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: _t.TimeoutType = None,
        verify: _t.VerifyType = True,
        cert: _t.CertType = None,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple or urllib3 Timeout object
        :param verify: (optional) Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case it
            must be a path to a CA bundle to use
        :para

-----------------------------------------------------------------

Final rank: 1
Ranks: {'vector': 1, 'bm25': 2}
Exact match: False
RRF score: 0.03252
Vector rank: 1
BM25 rank: 2
File: src/requests/adapters.py
Symbol: HTTPAdapter.add_headers
Lines: 599-611

Code preview:
HTTPAdapter.add_headers
    def add_headers(self, request: PreparedRequest, **kwargs: Any) -> None:
        """Add any headers needed by the connection. As of v2.0 this does
        nothing by default, but is left for overriding by users that subclass
        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass

-----------------------------------------------------------------
Final rank: 2
Ranks: {'vector': 4, 'bm25': 3}
Exact match: False
RRF score: 0.03150
Vector rank: 4
BM25 rank: 3
File: src/requests/adapters.py
Symbol: HTTPAdapter
Lines: 158-183

Code preview:
HTTPAdapter
class HTTPAdapter(BaseAdapter):
    """The built-in HTTP Adapter for urllib3.

    Provides a general-case interface for Requests sessions to contact HTTP and
    HTTPS urls by implementing the Transport Adapter interface. This class will
    usually be created by the :class:`Session <Session>` class under the
    covers.

    :param pool_connections: The number of urllib3 connection pools to cache.
    :param pool_maxsize: The maximum number of connections to save in the pool.
    :param max_retries: The maximum number of retries each connection
        should attempt. Note, this applies only to failed DNS lookups, socket
        connections and connection timeouts, never to requests where data has
        made it to the server. By default, Requests does not retry failed
        connections. If you need granular control over the conditions under
        which we retry a request, import urllib3's ``Retry`` class and pass
        that instead.
    :param pool_block: Whether 

-----------------------------------------------------------------
Final rank: 3
Ranks: {'vector': 3, 'bm25': 8}
Exact match: False
RRF score: 0.03058
Vector rank: 3
BM25 rank: 8
File: src/requests/adapters.py
Symbol: HTTPAdapter.get_connection
Lines: 512-553

Code preview:
HTTPAdapter.get_connection
    def get_connection(
        self, url: str, proxies: dict[str, str] | None = None
    ) -> HTTPConnectionPool:
        """DEPRECATED: Users should move to `get_connection_with_tls_context`
        for all subclasses of HTTPAdapter using Requests>=2.32.2.

        Returns a urllib3 connection for the given URL. This should not be
        called from user code, and is only exposed for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param url: The URL to connect to.
        :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        :rtype: urllib3.HTTPConnectionPool
        """
        warnings.warn(
            (
                "`get_connection` has been deprecated in favor of "
                "`get_connection_with_tls_context`. Custom HTTPAdapter subclasses "
                "will need to migrate for Requests>=2.32.2. Please see "
                "https://github.com/psf


**q2:** Explain Session.get_adapter

**Retreived results:**

Vector results: 10
BM25 results: 10
Exact matches: 1
Fused results: 17

Exact match ranking: 1

Final rank: 1
Ranks: {'vector': 1, 'bm25': 1, 'exact': 1}
Exact match: True
RRF score: 0.04918
Vector rank: 1
BM25 rank: 1
File: src/requests/sessions.py
Symbol: Session.get_adapter
Lines: 870-881

Code preview:
Session.get_adapter
    def get_adapter(self, url: str) -> BaseAdapter:
        """
        Returns the appropriate connection adapter for the given URL.

        :rtype: requests.adapters.BaseAdapter
        """
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix.lower()):
                return adapter

        # Nothing matches :-/
        raise InvalidSchema(f"No connection adapters were found for {url!r}")

-----------------------------------------------------------------
Final rank: 2
Ranks: {'vector': 4, 'bm25': 3}
Exact match: False
RRF score: 0.03150
Vector rank: 4
BM25 rank: 3
File: src/requests/sessions.py
Symbol: Session
Lines: 395-412

Code preview:
Session
class Session(SessionRedirectMixin):
    """A Requests session.

    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> import requests
      >>> s = requests.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>

    Or as a context manager::

      >>> with requests.Session() as s:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """

-----------------------------------------------------------------
Final rank: 3
Ranks: {'vector': 6, 'bm25': 2}
Exact match: False
RRF score: 0.03128
Vector rank: 6
BM25 rank: 2
File: src/requests/sessions.py
Symbol: Session.mount
Lines: 888-897

Code preview:
Session.mount
    def mount(self, prefix: str, adapter: BaseAdapter) -> None:
        """Registers a connection adapter to a prefix.

        Adapters are sorted in descending order by prefix length.
        """
        self.adapters[prefix] = adapter
        keys_to_move = [k for k in self.adapters if len(k) < len(prefix)]

        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)

-----------------------------------------------------------------

Eventhoug it has exact match ranked first, but the rankings of the both vector and bm25 search also ranked
first.

**q3:** Where does Requests follow HTTP redirects?

**Retrieved resutls:**

Vector results: 10
BM25 results: 10
Exact matches: 0
Fused results: 17

As expected, here there is no exact matches have been detected.

Final rank: 1
Ranks: {'vector': 1, 'bm25': 5}
Exact match: False
RRF score: 0.03178
Vector rank: 1
BM25 rank: 5
File: src/requests/auth.py
Symbol: HTTPDigestAuth.handle_redirect
Lines: 268-271

Code preview:
HTTPDigestAuth.handle_redirect
    def handle_redirect(self, r: Response, **kwargs: Any) -> None:
        """Reset num_401_calls counter on redirects."""
        if r.is_redirect:
            self._thread_local.num_401_calls = 1

-----------------------------------------------------------------
Final rank: 2
Ranks: {'vector': 3, 'bm25': 7}
Exact match: False
RRF score: 0.03080
Vector rank: 3
BM25 rank: 7
File: src/requests/models.py
Symbol: Response.is_redirect
Lines: 876-881

Code preview:
Response.is_redirect
    @property
    def is_redirect(self) -> bool:
        """True if this Response is a well-formed HTTP redirect that could have
        been processed automatically (by :meth:`Session.resolve_redirects`).
        """
        return "location" in self.headers and self.status_code in REDIRECT_STATI

-----------------------------------------------------------------
Final rank: 3
Ranks: {'vector': 8, 'bm25': 8}
Exact match: False
RRF score: 0.02941
Vector rank: 8
BM25 rank: 8
File: src/requests/api.py
Symbol: head
Lines: 102-114

Code preview:
head
def head(url: _t.UriType, **kwargs: Unpack[_t.RequestKwargs]) -> Response:
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes. If
        `allow_redirects` is not provided, it will be set to `False` (as
        opposed to the default :meth:`request` behavior).
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    kwargs.setdefault("allow_redirects", False)
    return request("head", url, **kwargs)

-----------------------------------------------------------------

**q4:** How does Requests send HTTP requests?

**Retreived results:**

Vector results: 10
BM25 results: 10
Exact matches: 0
Fused results: 17

Same as expected, no exact matches found.

-----------------------------------------------------------------
Final rank: 1
Ranks: {'vector': 5, 'bm25': 1}
Exact match: False
RRF score: 0.03178
Vector rank: 5
BM25 rank: 1
File: src/requests/adapters.py
Symbol: HTTPAdapter.add_headers
Lines: 599-611

Code preview:
HTTPAdapter.add_headers
    def add_headers(self, request: PreparedRequest, **kwargs: Any) -> None:
        """Add any headers needed by the connection. As of v2.0 this does
        nothing by default, but is left for overriding by users that subclass
        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass

-----------------------------------------------------------------
Final rank: 2
Ranks: {'vector': 6, 'bm25': 5}
Exact match: False
RRF score: 0.03054
Vector rank: 6
BM25 rank: 5
File: src/requests/api.py
Symbol: request
Lines: 24-71

Code preview:
request
def request(
    method: str, url: _t.UriType, **kwargs: Unpack[_t.RequestKwargs]
) -> Response:
    """Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'nam

-----------------------------------------------------------------
Final rank: 3
Ranks: {'vector': 3, 'bm25': 10}
Exact match: False
RRF score: 0.03016
Vector rank: 3
BM25 rank: 10
File: src/requests/models.py
Symbol: Request
Lines: 284-310

Code preview:
Request
class Request(RequestHooksMixin):
    """A user-created :class:`Request <Request>` object.

    Used to prepare a :class:`PreparedRequest <PreparedRequest>`, which is sent to the server.

    :param method: HTTP method to use.
    :param url: URL to send.
    :param headers: dictionary of headers to send.
    :param files: dictionary of {filename: fileobject} files to multipart upload.
    :param data: the body to attach to the request. If a dictionary or
        list of tuples ``[(key, value)]`` is provided, form-encoding will
        take place.
    :param json: json for the body to attach to the request (if files or data is not specified).
    :param params: URL parameters to append to the URL. If a dictionary or
        list of tuples ``[(key, value)]`` is provided, form-encoding will
        take place.
    :param auth: Auth handler or (user, pass) tuple.
    :param cookies: dictionary or CookieJar of cookies to attach to this request.
    :param hooks: dictionary of callb

-----------------------------------------------------------------

## After implementing weighted reciprocal rank fusion
Since standard RRF provides equal weights to every ranking system, even if the exact match is found,
the RRF ranks it lower with the influence of the other ranking models. So, experimented the system with the
weighted RRF. Here, a higher weight is given for the exact match ranking system. So, that if the exact
term matched (qualified name) then it is given a higher weight so that the relevance will be higher and it
helps to rank it higher up, so that it is retreived correctly.

Comparing the same question **Where is HTTPAdapter.send implemented?** with the RRF and WRRF.

With RRF, the obtained RRF score = 0.01639 and both the vector and the BM25 ranks were beyond 10.
Overall rank was 7.

Now with the implementation of WRRF,
Vector results: 10
BM25 results: 10
Exact matches: 1
Fused results: 16

=================================================================
HYBRID SEARCH RESULTS
=================================================================

-----------------------------------------------------------------
Final rank: 1
Ranks: {'exact': 1}
Exact match: True
RRF score: 0.04918
Vector rank: —
BM25 rank: —
File: src/requests/adapters.py
Symbol: HTTPAdapter.send
Lines: 634-748

Code preview:
HTTPAdapter.send
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: _t.TimeoutType = None,
        verify: _t.VerifyType = True,
        cert: _t.CertType = None,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple or urllib3 Timeout object
        :param verify: (optional) Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case it
            must be a path to a CA bundle to use
        :para

-----------------------------------------------------------------
Final rank: 2
Ranks: {'vector': 1, 'bm25': 2}
Exact match: False
RRF score: 0.03252
Vector rank: 1
BM25 rank: 2
File: src/requests/adapters.py
Symbol: HTTPAdapter.add_headers
Lines: 599-611

Code preview:
HTTPAdapter.add_headers
    def add_headers(self, request: PreparedRequest, **kwargs: Any) -> None:
        """Add any headers needed by the connection. As of v2.0 this does
        nothing by default, but is left for overriding by users that subclass
        the :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param request: The :class:`PreparedRequest <PreparedRequest>` to add headers to.
        :param kwargs: The keyword arguments from the call to send().
        """
        pass

-----------------------------------------------------------------
Final rank: 3
Ranks: {'vector': 4, 'bm25': 3}
Exact match: False
RRF score: 0.03150
Vector rank: 4
BM25 rank: 3
File: src/requests/adapters.py
Symbol: HTTPAdapter
Lines: 158-183

Code preview:
HTTPAdapter
class HTTPAdapter(BaseAdapter):
    """The built-in HTTP Adapter for urllib3.

    Provides a general-case interface for Requests sessions to contact HTTP and
    HTTPS urls by implementing the Transport Adapter interface. This class will
    usually be created by the :class:`Session <Session>` class under the
    covers.

    :param pool_connections: The number of urllib3 connection pools to cache.
    :param pool_maxsize: The maximum number of connections to save in the pool.
    :param max_retries: The maximum number of retries each connection
        should attempt. Note, this applies only to failed DNS lookups, socket
        connections and connection timeouts, never to requests where data has
        made it to the server. By default, Requests does not retry failed
        connections. If you need granular control over the conditions under
        which we retry a request, import urllib3's ``Retry`` class and pass
        that instead.
    :param pool_block: Whether 

-----------------------------------------------------------------

Weighted RRF successfully promoted the exact qualified-symbol
match from rank 7 to rank 1.

The exact retrieval contribution was increased using a weight
of 3.0, while vector and BM25 retained weights of 1.0.

WRRF improved exact-symbol retrieval for this experiment.
Further evaluation is required to determine its impact on
overall retrieval performance and natural-language queries.


## WRRF: Additional Query Experiments

### Query 2: Explain Session.get_adapter

Expected symbol:
Session.get_adapter

Result:
- Final rank: 1
- Vector rank: 1
- BM25 rank: 1
- Exact rank: 1
- WRRF score: 0.08197

Observation:
All three retrieval systems independently ranked the
correct symbol first. The exact-match contribution
increased the combined score to 0.08197.

### Query 3: Where does Requests follow HTTP redirects?

Expected symbol:
SessionRedirectMixin.resolve_redirects

Result:
- Final rank: 10
- Vector rank: 5
- BM25: Not in top 10
- Exact matches: 0

Observation:
The correct symbol was retrieved at rank 10.
Since no qualified identifier was present, exact
retrieval did not contribute to the ranking.

### Query 4: How does Requests send HTTP requests?

Result:
- Exact matches: 0
- Top result: HTTPAdapter.add_headers
- Session.request: Rank 7
- PreparedRequest: Rank 5

Observation:
The retrieval system identifies several relevant
components but does not yet provide a strong ranking
of the complete request execution flow.

### Overall WRRF observation

Weighted RRF successfully prioritizes exact qualified
symbol matches while preserving the standard RRF
calculation when no exact match is detected.

Further benchmark evaluation is required to establish
its overall retrieval performance.

## Weighted RRF evaluation
We are comparing the vector retreival, BM25 standard RRF, three-way equak weight RRF and
weighted RRF.

- Vector-only
- BM25-only
- Two-way RRF (vector + BM25)
- Three-way RRF (vector + BM25 + exact, equal weights)
- Weighted RRF (vector + BM25 + exact, exact weight = 3)

**Hypothesis:** Exact-symbol retreival should improve retreiavl when the user explicitly mentions
a qualified code identifier.

**Limitation:** The existing natural-language benchmark does not contain any qualified code identifier,
Therefore, exact-symbol retreival is expected to return no matches for this existing dataset.
A separate exact-symbol benchmark is required to evaluate the contribution of exact matching.

### Observation
**Normal dataset without exact symbol queries:**
==================================================
FINAL EVALUATION
==================================================

Method: BM25
Recall@3: 0.5000
Recall@5: 0.5500
MRR:      0.4042

Method: RRF
Recall@3: 0.5000
Recall@5: 0.5000
MRR:      0.5100

Method: RRF_EQUAL
Recall@3: 0.5000
Recall@5: 0.5000
MRR:      0.5100

Method: VECTOR
Recall@3: 0.3750
Recall@5: 0.4750
MRR:      0.4658

Method: WRRF
Recall@3: 0.5000
Recall@5: 0.5000
MRR:      0.5100

**Summary of the questions with the exact symbols**:
==================================================
FINAL EVALUATION
==================================================

Method: RRF_EQUAL
Recall@3: 0.8750
Recall@5: 0.8750
MRR:      0.8304

Method: WRRF
Recall@3: 1.0000
Recall@5: 1.0000
MRR:      1.0000

Method: BM25
Recall@3: 0.6250
Recall@5: 0.6250
MRR:      0.5139

Method: VECTOR
Recall@3: 0.6250
Recall@5: 0.6250
MRR:      0.5387

Method: RRF
Recall@3: 0.6250
Recall@5: 0.6250
MRR:      0.5804

### Findings

- WRRF did not improve natural-language retrieval.
- Three-way equal-weight RRF improved exact-symbol retrieval.
- Weighted RRF achieved perfect retrieval metrics on the
  eight-question exact-symbol benchmark.
- Exact-symbol matching is particularly useful when
  users provide qualified identifiers.

### Limitations

- The exact-symbol benchmark contains only 8 questions.
- Queries explicitly contain the target identifiers.
- Results are currently based on one Python repository.
- Further testing is required for nonexistent identifiers,
  ambiguous names and identifier variations.

### Conclusion

Weighted RRF shows promising results for exact code-symbol
lookup. It should be used as a complementary retrieval
mechanism rather than a replacement for semantic retrieval.

## Unified benchmark design

Dataset: benchmark_questions.jsonl
Target size: 40 questions

Categories:
- Natural language: 12
- Exact identifiers: 10
- Mixed queries: 10
- Vague / indirect: 8

Objective:
Evaluate retrieval performance across different
developer query styles using a common benchmark.

Evaluation:
- Recall@3
- Recall@5
- MRR
- Exact-match rank-1 accuracy
- Category-level performance

All retrieval configurations will use the same
benchmark questions and relevance labels.

Observations:
- WRRF achieved the highest overall scores.
- Exact identifier queries achieved perfect scores with WRRF.
- Mixed queries benefited substantially from exact matching.
- Natural-language results were unchanged by exact matching.
- Vague queries remain a significant retrieval weakness.

Limitations:
- Only one repository was evaluated.
- Benchmark contains 40 questions.
- Exact-match weight was selected using earlier experiments.
- Results are development results, not independent test results.

Next investigation:
- Analyse individual failed questions.
- Implement active retrieval and query rewriting.
- Compare retrieval performance before and after retries.

## Vague query analysis

Analysed Q33–Q40 across all five retrieval configurations.

Findings:
- WRRF and standard RRF produced identical results for all eight vague questions.
- Exact-symbol retrieval did not contribute because no qualified identifiers were present.
- Q34 and Q36 failed across all retrieval methods.
- Q33 and Q37 retrieved only one of two relevant symbols.
- Q39 retrieved relevant evidence at rank 9 with WRRF.
- BM25 performed particularly well on Q38, retrieving the relevant symbol at rank 1.
- Fusion does not consistently improve individual query rankings.

Identified failure categories:
1. Missing evidence.
2. Weak ranking.
3. Incomplete evidence.

Future investigation:
- Query rewriting.
- Query decomposition.
- Retrieval quality assessment.
- Iterative retrieval and evidence comparison.

## Active RAG - LLM Assessment Milestone

LLM Provider: Groq
Model: GPT-OSS 20B

Implemented:
- Groq API integration
- Structured LLM evidence assessment
- Relevance and sufficiency evaluation
- Missing-information identification
- Refined query generation
- Deterministic assessment validation

Validation:
- 10 new assessment validation tests
- 76 total automated tests passed

Observation:
The LLM can inspect retrieved code evidence and produce
structured relevance assessments. Deterministic validation
ensures that the returned assessment follows the expected
logical rules.

Note:
Retrieval performance improvement has not yet been established.