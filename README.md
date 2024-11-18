[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">

  <h1 align="center">Middleware - Python APM</h1>

  <p align="center">
    An Application Performance Monitoring (APM) tool for Python applications and libraries
    <br />
    <a href="https://docs.middleware.io/apm-configuration/python"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/middleware-labs/agent-apm-python/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/middleware-labs/agent-apm-python/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

## About

[![Product Name Screen Shot][product-screenshot]](https://middleware.io/)

Middleware's APM (Application Performance Monitoring) tool offers a comprehensive solution for developers seeking to enhance the performance and observability of their Python applications.

By installing the Middleware Host Agent and integrating the APM package, developers can seamlessly monitor applications, capturing distributed tracing data, metrics, logs, and profiling information. This enables a thorough view of application performance and behavior.

For detailed instructions on installing the Middleware Host Agent and integrating the APM package, refer to our [documentation](https://docs.middleware.io/apm-configuration/python) for Python applications.

Latest release built with:

- [OpenTelemetry version 1.27.0/0.48b0](https://github.com/open-telemetry/opentelemetry-python/releases/tag/v1.27.0)

Requirements

- Python 3.8 or higher

# Installation

Run the following command in your terminal:

```shell
pip install middleware-io
```

To install with **Continuous Profiling** support:

```shell
pip install middleware-io[profiling]
```

For further details on prerequisites, configuration options, and use, visit our docs page at [https://docs.middleware.io/apm-configuration/python](https://docs.middleware.io/apm-configuration/python).  

For framwork based python instrumentation examples, visit github repo at  [https://github.com/middleware-labs/demo-apm-python](https://github.com/middleware-labs/demo-apm-python).

<!-- LICENSE -->
## License

Distributed under the Apache License. See `LICENSE` for more information.

[contributors-shield]: https://img.shields.io/github/contributors/middleware-labs/agent-apm-python.svg?style=for-the-badge
[contributors-url]: https://github.com/middleware-labs/agent-apm-python/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/middleware-labs/agent-apm-python.svg?style=for-the-badge
[forks-url]: https://github.com/middleware-labs/agent-apm-python/network/members
[stars-shield]: https://img.shields.io/github/stars/middleware-labs/agent-apm-python.svg?style=for-the-badge
[stars-url]: https://github.com/middleware-labs/agent-apm-python/stargazers
[issues-shield]: https://img.shields.io/github/issues/middleware-labs/agent-apm-python.svg?style=for-the-badge
[issues-url]: https://github.com/middleware-labs/agent-apm-python/issues
[license-shield]: https://img.shields.io/github/license/middleware-labs/agent-apm-python.svg?style=for-the-badge
[license-url]: https://github.com/middleware-labs/agent-apm-python/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/middleware-labs
[product-screenshot]: ./product.png
