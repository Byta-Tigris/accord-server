from datetime import datetime
from unittest import TestCase

from digger.youtube.types import MetricRecord, YTMetrics


class TestYTMetric(TestCase):

    def test_yt_metric_format_argument(self) -> None:
        fixtures = [
            ["views", "views"],
            ["estimateMinutesWatched", "estimate_minutes_watched"],
            ["annotationCloseRate", "annotation_close_rate"],
            ["AnnotateMe", "_annotate_me"]
        ]
        for fixture in fixtures:
            self.assertEqual(YTMetrics.format_argument(fixture[0]), fixture[1])

    def test_yt_metrics_class(self) -> None:
        sharing_service_fixture = {"columnHeaders": [
                {
                    "name": "sharingService",
                    "columnType": "DIMENSION",
                    "dataType": "STRING"
                },
                {
                    "name": "shares",
                    "columnType": "METRIC",
                    "dataType": "INTEGER"
                }
            ],
                "rows": [
                [
                    "WHATS_APP",
                    2
                ],
                [
                    "OTHER",
                    1
                ],
                [
                    "COPY_PASTE",
                    8
                ]
            ],
            }
        # breakpoint()
        sharing_metric = YTMetrics.from_yt_response(sharing_service_fixture["columnHeaders"], sharing_service_fixture["rows"])
        self.assertNotEqual(sharing_metric.shares, None)
        self.assertEqual(len(sharing_metric.shares), 1)


        
        subscribed_status_fixture = {
                "columnHeaders": [
                    {
                        "name": "subscribedStatus",
                        "columnType": "DIMENSION",
                        "dataType": "STRING"
                    },
                    {
                        "name": "day",
                        "columnType": "DIMENSION",
                        "dataType": "STRING"
                    },
                    {
                        "name": "views",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    },
                    {
                        "name": "estimatedMinutesWatched",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    },
                    {
                        "name": "averageViewDuration",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    }
                ],
                "rows": [
                    [
                        "UNSUBSCRIBED",
                        "2020-10-07",
                        5,
                        2,
                        29
                    ],
                    [
                        "SUBSCRIBED",
                        "2020-10-22",
                        2,
                        1,
                        47
                    ],
                    [
                        "SUBSCRIBED",
                        "2020-10-24",
                        3,
                        1,
                        24
                    ],
                    [
                        "SUBSCRIBED",
                        "2021-01-16",
                        1,
                        0,
                        2
                    ]
                ]
            }
        # breakpoint()
        subscribed_metric = YTMetrics.from_yt_response(subscribed_status_fixture["columnHeaders"], subscribed_status_fixture["rows"])
        self.assertNotEqual(subscribed_metric.views, None)
        self.assertNotEqual(subscribed_metric.estimated_minutes_watched, None)
        self.assertNotEqual(subscribed_metric.average_view_duration, None)
        self.assertGreater(len(subscribed_metric.views), 0)
        self.assertTrue("UNSUBSCRIBED" in subscribed_metric.views["2020-10-07"])
        self.assertEqual(subscribed_metric.average_view_duration["2020-10-22"]["SUBSCRIBED"], 47)


        time_based_fixture = {
            
                "columnHeaders": [
                    {
                        "name": "day",
                        "columnType": "DIMENSION",
                        "dataType": "STRING"
                    },
                    {
                        "name": "views",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    },
                    {
                        "name": "estimatedMinutesWatched",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    },
                    {
                        "name": "averageViewDuration",
                        "columnType": "METRIC",
                        "dataType": "INTEGER"
                    }
                ],
                "rows": [
                    [
                        "2020-10-07",
                        5,
                        2,
                        29
                    ],
                    [
                        "2020-10-08",
                        6,
                        4,
                        44
                    ]
                ]
            }
        # breakpoint()
        time_based_metric = YTMetrics.from_yt_response(time_based_fixture["columnHeaders"], time_based_fixture["rows"])
        self.assertNotEqual(time_based_metric.views, None)
        self.assertTrue("2020-10-07" in time_based_metric.estimated_minutes_watched)
        self.assertEqual(time_based_metric.average_view_duration["2020-10-08"]["TOTAL"], 44)

 
class TestMetricRecord(TestCase):

    age_gender_fixtures = [
        {
            "day": "2020-10-07",
            "gender": "M",
            "metric": "age18_24",
            "value": 0.33
        },
        {
            "day": "2020-10-07",
            "gender": "M",
            "metric": "age24_36",
            "value": 0.68
        },
        {
            "day": "2020-10-07",
            "gender": "F",
            "metric": "age18_24",
            "value": 0.33
        },
        {
            "day": "2020-10-08",
            "gender": "M",
            "metric": "age18_24",
            "value": 0.33
        },
    ]

    subscribed_metrics_fixture = [
        {
            "day": "2020-10-07",
            "metric": "UNSUBSCRIBED",
            "value": 26
        },
        {
            "day": "2020-10-07",
            "metric": "SUBSCRIBED",
            "value": 28
        },
        {
            "day": "2020-10-07",
            "metric": "TOTAL",
            "value": 28
        },
        {
            "day": "2020-10-07",
            "metric": "UNSUBSCRIBED",
            "value": 29
        },
        {
            "day": "2020-10-08",
            "metric": "UNSUBSCRIBED",
            "value": 36
        },
        {
            "day": "2020-10-07",
            "metric": "SUBSCRIBED",
            "value": 26
        },
    ]


    def test_add(self) -> None:
        
        ## Testing subscribed_metrics_fixture
        subs_metric_record = MetricRecord(
            "metric", "value", ["day"]
        )
        
        for fixture in self.subscribed_metrics_fixture:
            subs_metric_record.add(**fixture)
        self.assertTrue("2020-10-07" in subs_metric_record)
        self.assertTrue("2020-10-07.SUBSCRIBED" in subs_metric_record)
        self.assertEqual(subs_metric_record["2020-10-08.UNSUBSCRIBED"], 36)
        
        ## Testing age gender_metric_fixture
        age_gender_record = MetricRecord("metric", "value", ["day", "gender"])
        # for fixture in self.age_gender_fixtures:
        # breakpoint()
        age_gender_record.extend(self.age_gender_fixtures)
        self.assertTrue("2020-10-07" in age_gender_record)
        self.assertTrue("2020-10-07.M.age18_24" in age_gender_record)
        self.assertEqual("2020-10-07.M.age24_36", 0.68)
            
        
            