import json
import logging

import pytest
from medkit.core import Attribute
from medkit.core.text import TextDocument, Entity, Relation, Span
from medkit.io import DoccanoTask, DoccanoOutputConverter


def _get_doc_by_task(task: DoccanoTask):
    # get a TextDocument by task, seqlabeling and relationextraction use
    # the same doc, the output format changes
    doc = TextDocument(text="medkit was created in 2022")

    if task == DoccanoTask.RELATION_EXTRACTION or task == DoccanoTask.SEQUENCE_LABELING:
        medkit_anns = [
            Entity(label="ORG", spans=[Span(0, 6)], text="medkit", uid="e1"),
            Entity(label="DATE", spans=[Span(22, 26)], text="2022", uid="e2"),
            Relation(label="created_in", source_id="e1", target_id="e2", uid="r1"),
        ]

        for ann in medkit_anns:
            doc.anns.add(ann)

    elif task == DoccanoTask.TEXT_CLASSIFICATION:
        attr = Attribute(label="category", value="header")
        doc.raw_segment.attrs.add(attr)
    return doc


EXPECTED_DOCLINE_BY_TASK = {
    DoccanoTask.RELATION_EXTRACTION: {
        "id": 0,
        "text": "medkit was created in 2022",
        "entities": [
            {"id": 0, "start_offset": 0, "end_offset": 6, "label": "ORG"},
            {"id": 1, "start_offset": 22, "end_offset": 26, "label": "DATE"},
        ],
        "relations": [{"id": 0, "from_id": 0, "to_id": 1, "type": "created_in"}],
    },
    # json does not recognize tuples
    # NOTE: this works with doccano IDE
    DoccanoTask.SEQUENCE_LABELING: {
        "text": "medkit was created in 2022",
        "label": [[0, 6, "ORG"], [22, 26, "DATE"]],
    },
    DoccanoTask.TEXT_CLASSIFICATION: {
        "text": "medkit was created in 2022",
        "label": ["header"],
    },
}


@pytest.mark.parametrize(
    "task",
    [
        DoccanoTask.RELATION_EXTRACTION,
        DoccanoTask.TEXT_CLASSIFICATION,
        DoccanoTask.SEQUENCE_LABELING,
    ],
)
def test_save_by_task(tmp_path, task):
    converter = DoccanoOutputConverter(task=task, attr="category")
    dir_path = tmp_path / task.value
    expected_jsonl_path = dir_path / "all.jsonl"

    medkit_docs = [_get_doc_by_task(task)]
    converter.save(medkit_docs, dir_path=dir_path)

    assert dir_path.exists()
    assert expected_jsonl_path.exists()

    with open(expected_jsonl_path) as fp:
        data = json.load(fp)

    assert data == EXPECTED_DOCLINE_BY_TASK[task]


def test_warnings(tmp_path, caplog):
    task = DoccanoTask.RELATION_EXTRACTION
    converter = DoccanoOutputConverter(task=task, anns_labels=["ORG", "created_in"])
    dir_path = tmp_path / task.value

    medkit_docs = [_get_doc_by_task(task)]
    with caplog.at_level(logging.WARNING, logger="medkit.io.doccano"):
        converter.save(medkit_docs, dir_path=dir_path)
        assert "Entity source/target was no found" in caplog.text

    with caplog.at_level(logging.WARNING, logger="medkit.io.doccano"):
        DoccanoOutputConverter(task=DoccanoTask.TEXT_CLASSIFICATION)
        assert "You should specify an attribute label" in caplog.text

    with pytest.raises(KeyError, match="The attribute with the corresponding .*"):
        converter = DoccanoOutputConverter(
            task=DoccanoTask.TEXT_CLASSIFICATION, attr="is_negated"
        )
        converter.save(medkit_docs, dir_path=dir_path)
