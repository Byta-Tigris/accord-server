from datetime import datetime
from unittest import TestCase

from digger.youtube.types import YTMetrics
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

 
