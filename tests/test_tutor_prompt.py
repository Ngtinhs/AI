import unittest

from prompts.tutor_prompt import DEFAULT_LEVEL, LEARNER_CONTEXT, build_learner_context, build_tutor_prompt


class TestLearnerLevelInPrompt(unittest.TestCase):
    def test_no_placement_test_uses_default_level(self):
        context = build_learner_context(None)
        self.assertEqual(context["english_level"], DEFAULT_LEVEL)

    def test_placement_level_is_used(self):
        context = build_learner_context("B1")
        self.assertEqual(context["english_level"], "B1")

    def test_default_context_is_not_changed(self):
        build_learner_context("B2")
        self.assertEqual(LEARNER_CONTEXT["english_level"], DEFAULT_LEVEL)

    def test_prompt_contains_level_and_no_hardcoded_a2(self):
        prompt = build_tutor_prompt(build_learner_context("B2"), "Hello world.")
        self.assertIn("English level: B2", prompt)
        self.assertIn("suitable for a B2 learner", prompt)
        self.assertNotIn("A2", prompt)


if __name__ == "__main__":
    unittest.main()
