from datetime import timedelta
from typing import Dict, List, Union
from pandas import DataFrame, Timestamp

from insights.models import SocialMediaHandleMetrics
from utils import date_to_string, string_to_date

Number = Union[int, float]
MetricTableJson = Dict[str, Union[List[str], List[Union[str, Number]], Dict[str, Number]]]


class MetricTable:
    """
    Columns are Date and all other metrics explicity
    Each Metric must implement get_metric_rows which returns dict with date as key and dict as value containign metric_name as key and data as value.
    Each Metric Class must have a get_columns staticmenthod, which will return all column names
    If earliest metric contains prev_totals in metrics
        than prev_totals will be formed into row with date one day prior to the earliest 
        then metrics get_prev_totals_row will be used
    """
    def __init__(self,columns = None, index: str = "day", *metrics: SocialMediaHandleMetrics, **kwargs) -> None:
        self.metrics = metrics
        self.columns = columns
        self.index = index
        self._df = DataFrame(columns=columns)

        if columns is None and len(metrics) > 0:
            self.columns = metrics[0].get_columns()
        for metric in metrics:
            self.add(metric)
    
    @property
    def df(self) -> DataFrame:
        return self._df
    

    def transform_row_dict(self, data: Dict[str, Dict[str, Union[int, float]]]) -> List[Dict[str, Union[int, float]]]:
        transformed = []
        for key, value in data.items():
            value[self.index] = string_to_date(key)
            transformed.append(value.copy())
        return transformed

    def reset_prev_totals(self, metric: SocialMediaHandleMetrics) -> None:
        oldest_date = self._df[self.index].min()
        if oldest_date and isinstance(oldest_date, Timestamp):
            oldest_date = oldest_date.to_pydatetime()
        elif oldest_date and isinstance(oldest_date, str):
            oldest_date = string_to_date(oldest_date)
        if metric.expired_on <= oldest_date and "prev_totals" in metric.meta_data:
            metric_data: Dict[str, Union[int, float]] = metric.get_prev_totals_row()
            new_earliest_date = metric.created_on - timedelta(days=1)
            rows = self.transform_row_dict({date_to_string(new_earliest_date): metric_data})
            self.add_rows(rows)


    def add_rows(self, rows: List[List[str, Number]]) -> None:
        model_row = {key: 0  for key in self.columns if key != self.index}
        for row in rows:
            self._df.append(model_row | row, ignore_index=True)
                    
    
    def add(self, metric: SocialMediaHandleMetrics) -> None:
        metric_data: Dict[str, Dict[str, Union[int, float]]] = metric.get_metric_rows()
        rows = self.transform_row_dict(metric_data)
        self.add_rows(rows)
        self.reset_prev_totals(metric)
    
    def get_totals(self) -> Dict[str, Number]:
        totals = {}
        for col in self.columns:
            if col == self.index:
                continue
            totals[col] = self._df[col].sum()
        return totals
    
    def json(self) -> MetricTableJson:
        _json: MetricTableJson = {"columns": self.columns, "rows": [], "totals": self.get_totals()}
        for row in self._df.values:
            _json["rows"].append(list(row))
        return _json


    

    