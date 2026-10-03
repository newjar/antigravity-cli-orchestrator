import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import token_usage


class TokenUsageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.brain_dir = Path(self.temp_dir) / "brain"
        self.brain_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def create_mock_session(self, conv_id, steps, created_date="2026-10-03T10:00:00Z"):
        conv_dir = self.brain_dir / conv_id / ".system_generated" / "logs"
        conv_dir.mkdir(parents=True)
        transcript_file = conv_dir / "transcript.jsonl"
        with transcript_file.open("w", encoding="utf-8") as f:
            for step in steps:
                f.write(json.dumps(step) + "\n")
        return transcript_file

    def test_empty_usage(self):
        usage = token_usage.empty_usage()
        self.assertEqual(usage["input_tokens"], 0)
        self.assertEqual(usage["cache_read_tokens"], 0)
        self.assertEqual(usage["output_tokens"], 0)
        self.assertEqual(usage["total_tokens"], 0)

    def test_add_usage(self):
        target = token_usage.empty_usage()
        step_usage = {
            "input_tokens": 100,
            "cache_read_tokens": 20,
            "output_tokens": 50,
        }
        token_usage.add_usage(target, step_usage)
        self.assertEqual(target["input_tokens"], 100)
        self.assertEqual(target["cache_read_tokens"], 20)
        self.assertEqual(target["output_tokens"], 50)
        self.assertEqual(target["total_tokens"], 150)

    def test_parse_single_thread(self):
        conv_id = "root-session-1234"
        steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-10-03T10:00:00Z",
                "content": "Implement user authentication",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-10-03T10:00:05Z",
                "input_tokens": 1500,
                "cache_read_tokens": 500,
                "output_tokens": 200,
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "Role": "Backend Explorer",
                                    "TypeName": "research",
                                    "Model": "gemini-3.8-flash-high",
                                    "Prompt": "Explore auth path",
                                }
                            ]
                        },
                    }
                ],
            },
        ]
        self.create_mock_session(conv_id, steps)

        session_data = token_usage.analyze_session(conv_id, self.brain_dir)
        self.assertEqual(session_data["id"], conv_id)
        self.assertEqual(session_data["title"], "Implement user authentication")
        self.assertEqual(session_data["total"]["input_tokens"], 1500)
        self.assertEqual(session_data["total"]["cache_read_tokens"], 500)
        self.assertEqual(session_data["total"]["output_tokens"], 200)
        self.assertEqual(session_data["total"]["total_tokens"], 1700)
        self.assertIn("root", session_data["roles"])

    def test_linked_subagents_aggregation(self):
        root_id = "11111111-1111-1111-1111-111111111111"
        sub_id = "22222222-2222-2222-2222-222222222222"

        root_steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-10-03T10:00:00Z",
                "content": "Complex refactor",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-10-03T10:00:05Z",
                "input_tokens": 1000,
                "cache_read_tokens": 0,
                "output_tokens": 100,
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "Role": "Worker Agent",
                                    "TypeName": "self",
                                    "Model": "gemini-3.1-pro-high",
                                    "Prompt": "Refactor module",
                                }
                            ]
                        },
                    }
                ],
            },
            {
                "step_index": 2,
                "source": "SYSTEM",
                "type": "MESSAGE",
                "created_at": "2026-10-03T10:01:00Z",
                "content": f"Subagent {sub_id} finished",
            },
        ]

        sub_steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-10-03T10:00:10Z",
                "content": "Refactor module",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-10-03T10:00:50Z",
                "input_tokens": 2000,
                "cache_read_tokens": 1000,
                "output_tokens": 300,
            },
        ]

        self.create_mock_session(root_id, root_steps)
        self.create_mock_session(sub_id, sub_steps)

        session_data = token_usage.analyze_session(root_id, self.brain_dir)
        self.assertEqual(session_data["total"]["input_tokens"], 3000)
        self.assertEqual(session_data["total"]["cache_read_tokens"], 1000)
        self.assertEqual(session_data["total"]["output_tokens"], 400)
        self.assertEqual(session_data["total"]["total_tokens"], 3400)

    def test_list_sessions(self):
        conv_id = "session-abc"
        steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-10-03T10:00:00Z",
                "content": "List test prompt",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-10-03T10:00:05Z",
                "input_tokens": 100,
                "cache_read_tokens": 0,
                "output_tokens": 50,
            },
        ]
        self.create_mock_session(conv_id, steps)

        sessions = list(token_usage.list_sessions(self.brain_dir))
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["id"], conv_id)
        self.assertEqual(sessions[0]["title"], "List test prompt")

    def test_format_markdown_report(self):
        conv_id = "session-xyz"
        steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-10-03T10:00:00Z",
                "content": "Verify formatting",
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-10-03T10:00:05Z",
                "input_tokens": 500,
                "cache_read_tokens": 100,
                "output_tokens": 50,
            },
        ]
        self.create_mock_session(conv_id, steps)
        data = token_usage.analyze_session(conv_id, self.brain_dir)
        report = token_usage.format_markdown(data)
        self.assertIn("# Antigravity Token Usage Report", report)
        self.assertIn("session-xyz", report)
        self.assertIn("550", report)


if __name__ == "__main__":
    unittest.main()
