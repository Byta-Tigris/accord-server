from datetime import datetime
from unittest import TestCase

from digger.youtube.types import MetricRecord, YTMetrics
from utils import YOUTUBE_RESPONSE_DATE_FORMAT


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
        sharing_metric = YTMetrics(sharing_service_fixture["columnHeaders"], sharing_service_fixture["rows"])
        self.assertNotEqual(sharing_metric.shares,None)
        self.assertGreater(len(sharing_metric.shares), 0)
        self.assertEqual(len(sharing_metric.shares), 3)
        self.assertTrue("sharing_service" in sharing_metric.shares[0])
        self.assertEqual(sharing_metric.shares[0]["sharing_service"],"WHATS_APP" )
        self.assertEqual(sharing_metric.shares[2]["value"], 8)
        
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
        subscribed_metric = YTMetrics(subscribed_status_fixture["columnHeaders"], subscribed_status_fixture["rows"])
        self.assertNotEqual(subscribed_metric.views, None)
        self.assertNotEqual(subscribed_metric.estimated_minutes_watched, None)
        self.assertNotEqual(subscribed_metric.average_view_duration, None)
        self.assertGreater(len(subscribed_metric.views), 0)
        self.assertTrue("subscribed_status" in subscribed_metric.views[0])
        self.assertEqual(subscribed_metric.views[0]["subscribed_status"], "UNSUBSCRIBED")
        self.assertTrue("day" in subscribed_metric.estimated_minutes_watched[0])
        self.assertEqual(subscribed_metric.average_view_duration[1]["value"], 47)


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
        time_based_metric = YTMetrics(time_based_fixture["columnHeaders"], time_based_fixture["rows"])
        self.assertNotEqual(time_based_metric.views, None)
        self.assertTrue("day" in time_based_metric.estimated_minutes_watched[0])
        self.assertEqual(time_based_metric.views[0]["day"], datetime.strptime("2020-10-07", YOUTUBE_RESPONSE_DATE_FORMAT))
        self.assertEqual(time_based_metric.average_view_duration[1]["value"], 44)

 
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
            self.assertTrue(fixture["day"] in subs_metric_record)
            self.assertTrue(fixture["metric"] in subs_metric_record[fixture["day"]])
            self.assertEqual(subs_metric_record[fixture["day"]][fixture["metric"]], fixture["value"])
            self.assertTrue(f"{fixture['day']}__{fixture['metric']}" in subs_metric_record)
            self.assertEqual(subs_metric_record.get(f"{fixture['day']}__{fixture['metric']}"), fixture['value'])
        
        ## Testing age gender_metric_fixture
        age_gender_record = MetricRecord("metric", "value", ["day", "gender"])
        for fixture in self.age_gender_fixtures:
            age_gender_record.add(**fixture)
            self.assertTrue(fixture["day"] in age_gender_record)
            self.assertTrue(fixture["gender"] in age_gender_record[fixture["day"]])
            self.assertEqual(fixture["metric"] in age_gender_record[fixture["day"], fixture["gender"]], True)
            self.assertEqual(age_gender_record[fixture["day"], fixture["gender"], fixture["metric"]], fixture["value"])
        
            

    def test_convert_kwargs_to_row(self) -> None:
        subs_metric_record = MetricRecord(
            "metric", "value", ["day"]
        )
        for fix in self.subscribed_metrics_fixture:
            self.assertListEqual([fix["day"], fix["metric"], fix["value"]], subs_metric_record.convert_kwargs_to_row(**fix))

    def test_add_data_to_df(self) -> None:
        age_gender_record = MetricRecord("metric", "value", ["day", "gender"])
        for fixture in self.age_gender_fixtures:
            age_gender_record.add(in_df=True,**fixture)
        d = age_gender_record.df[age_gender_record.df.gender == "M"]
        self.assertGreater(len(d), 2)