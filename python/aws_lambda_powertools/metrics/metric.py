import json
import logging
from contextlib import contextmanager
from typing import Dict

from aws_lambda_powertools.helper.models import MetricUnit
from aws_lambda_powertools.metrics.base import MetricManager

logger = logging.getLogger(__name__)


class SingleMetric(MetricManager):
    """SingleMetric creates an EMF object with a single metric.

    EMF specification doesn't allow metrics with different dimensions.
    SingleMetric overrides MetricManager's add_metric method to do just that.

    Use `single_metric` when you need to create metrics with different dimensions,
    otherwise `aws_lambda_powertools.metrics.metrics.Metrics` is
    a more cost effective option

    Environment variables
    ---------------------
    POWERTOOLS_METRICS_NAMESPACE : str
        metric namespace

    Example
    -------
    **Creates cold start metric with function_version as dimension**

        from aws_lambda_powertools.metrics import SingleMetric, MetricUnit
        import json
        metric = Single_Metric()

        metric.add_namespace(name="ServerlessAirline")
        metric.add_metric(name="ColdStart", unit=MetricUnit.Count, value=1)
        metric.add_dimension(name="function_version", value=47)

        print(json.dumps(metric.serialize_metric_set(), indent=4))

    Parameters
    ----------
    MetricManager : MetricManager
        Inherits from `aws_lambda_powertools.metrics.base.MetricManager`
    """

    def add_metric(self, name: str, unit: MetricUnit, value: float):
        """Method to prevent more than one metric being created

        Parameters
        ----------
        name : str
            Metric name (e.g. BookingConfirmation)
        unit : MetricUnit
            Metric unit (e.g. "Seconds", MetricUnit.Seconds)
        value : float
            Metric value
        """
        if len(self.metric_set) > 0:
            logger.debug(f"Metric {name} already set, skipping...")
            return
        return super().add_metric(name, unit, value)


@contextmanager
def single_metric(name: str, unit: MetricUnit, value: float):
    """Context manager to simplify creation of a single metric

    Example
    -------
    **Creates cold start metric with function_version as dimension**

        from aws_lambda_powertools.metrics import single_metric, MetricUnit

        with single_metric(name="ColdStart", unit=MetricUnit.Count, value=1) as metric:
                metric.add_namespace(name="ServerlessAirline")
                metric.add_dimension(name="function_version", value=47)

    **Same as above but set namespace using environment variable**

        $ export POWERTOOLS_METRICS_NAMESPACE="ServerlessAirline"

        from aws_lambda_powertools.metrics import single_metric, MetricUnit

        with single_metric(name="ColdStart", unit=MetricUnit.Count, value=1) as metric:
                metric.add_dimension(name="function_version", value=47)

    Parameters
    ----------
    name : str
        Metric name
    unit : MetricUnit
        `aws_lambda_powertools.helper.models.MetricUnit`
    value : float
        Metric value

    Yields
    -------
    SingleMetric
        SingleMetric class instance

    Raises
    ------
    e
        Propagate error received
    """
    metric_set = None
    try:
        metric: SingleMetric = SingleMetric()
        metric.add_metric(name=name, unit=unit, value=value)
        yield metric
        logger.debug("Serializing single metric")
        metric_set: Dict = metric.serialize_metric_set()
    finally:
        logger.debug("Publishing single metric", {"metric": metric})
        print(json.dumps(metric_set))
