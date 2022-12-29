import { Field, useFormikContext } from "formik";
import { number, shape, string } from "prop-types";
import React, { useEffect } from "react";
import { useWizard } from "react-use-wizard";
import { usePageData } from "../../context/page-data-context";
import Button from "../Button";

function OneCodelist({ codelist, date }) {
  return (
    <p className="max-w-prose text-lg">
      Report will show the number of people who have had{" "}
      <a
        href={`https://www.opencodelists.org/codelist/${codelist.value}`}
        rel="noopener noreferrer"
        target="_blank"
      >
        {codelist.label}
      </a>{" "}
      added to their health record in the period between 1st September 2019 and{" "}
      {date}.
    </p>
  );
}

function CodelistBuilder({ date }) {
  const {
    state: { data },
  } = usePageData();
  const { values, setFieldValue } = useFormikContext();

  useEffect(() => {
    setFieldValue("codelistA", values?.codelistA || values.codelist0.value);
    setFieldValue("codelistB", values?.codelistB || values.codelist1.value);
    setFieldValue("timeValue", values.timeValue || 3);
    setFieldValue("timeScale", values.timeScale || "weeks");
    setFieldValue("timeEvent", values.timeEvent || "before");
  }, []);

  const handleChange = (e) => {
    if (e.target.name === "codelistA") {
      setFieldValue("codelistB", values.codelistA);
      setFieldValue("codelistA", e.target.value);
    }
    if (e.target.name === "codelistB") {
      setFieldValue("codelistA", values.codelistB);
      setFieldValue("codelistB", e.target.value);
    }
  };

  return (
    <>
      <p className="max-w-prose text-lg mb-2">The number of people who had</p>
      <Field as="select" name="codelistA" onChange={(e) => handleChange(e)}>
        <option value={values.codelist0.value}>{values.codelist0.label}</option>
        <option value={values.codelist1.value}>{values.codelist1.label}</option>
      </Field>
      <p className="max-w-prose text-lg py-2">
        added to their health record in the period between 1st September 2019
        and {date}, who have also had
      </p>
      <Field as="select" name="codelistB" onChange={(e) => handleChange(e)}>
        <option value={values.codelist0.value}>{values.codelist0.label}</option>
        <option value={values.codelist1.value}>{values.codelist1.label}</option>
      </Field>
      <p className="max-w-prose text-lg py-2">
        added to their health record at most
      </p>
      <Field name="timeValue" type="number" />
      <Field as="select" name="timeScale">
        <option value="weeks">Weeks</option>
        <option value="months">Months</option>
        <option value="years">Years</option>
      </Field>
      <Field as="select" name="timeEvent">
        <option value="before">Before</option>
        <option value="after">After</option>
      </Field>
      <p className="max-w-prose text-lg py-2">
        {data.find((item) => item.value === values?.codelistA)?.label}.
      </p>
    </>
  );
}

function Step2({ codelistCount }) {
  const { values } = useFormikContext();
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      <h1 className="text-4xl font-bold mb-4">Your report will show</h1>
      {codelistCount === 1 ? (
        <OneCodelist codelist={values.codelist0} date="7th December 2022" />
      ) : null}
      {codelistCount > 1 ? (
        <CodelistBuilder codelist={values.codelist0} date="7th December 2022" />
      ) : null}
      <div className="flex flex-row w-full gap-2 mt-10">
        <Button onClick={() => nextStep()}>Next</Button>
        <Button onClick={() => previousStep()} variant="danger">
          Go back
        </Button>
      </div>
    </>
  );
}

export default Step2;

Step2.propTypes = {
  codelistCount: number.isRequired,
};

OneCodelist.propTypes = {
  codelist: shape({
    label: string.isRequired,
    value: string.isRequired,
    organisation: string.isRequired,
  }).isRequired,
  date: string.isRequired,
};
