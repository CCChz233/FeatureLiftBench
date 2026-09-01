from __future__ import annotations

from featurelifted import BpmnParser, BpmnWorkflow

SCRIPT_BPMN = b"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" targetNamespace="http://example.test">
  <bpmn:process id="tiny" isExecutable="true">
    <bpmn:startEvent id="start"/>
    <bpmn:sequenceFlow id="f1" sourceRef="start" targetRef="script"/>
    <bpmn:scriptTask id="script" name="add">
      <bpmn:script>result = 1 + 2</bpmn:script>
    </bpmn:scriptTask>
    <bpmn:sequenceFlow id="f2" sourceRef="script" targetRef="end"/>
    <bpmn:endEvent id="end"/>
  </bpmn:process>
</bpmn:definitions>
"""


def test_script_process_completes() -> None:
    parser = BpmnParser()
    parser.add_bpmn_str(SCRIPT_BPMN)
    workflow = BpmnWorkflow(parser.get_spec("tiny"))
    workflow.do_engine_steps()
    assert workflow.is_completed() is True


def test_script_writes_result_data() -> None:
    parser = BpmnParser()
    parser.add_bpmn_str(SCRIPT_BPMN)
    workflow = BpmnWorkflow(parser.get_spec("tiny"))
    workflow.do_engine_steps()
    assert workflow.data["result"] == 3
