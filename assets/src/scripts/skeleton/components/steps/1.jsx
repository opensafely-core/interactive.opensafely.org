import { Field, useFormikContext } from "formik";
import { func, number } from "prop-types";
import React from "react";
import { useWizard } from "react-use-wizard";
import SelectCodelist from "../SelectCodelist";

function Step1({ codelistCount, setCodelistCount }) {
  const { isValid, setFieldValue, validateForm } = useFormikContext();
  const { nextStep } = useWizard();

  const handleAddCodelist = () => {
    setCodelistCount(codelistCount + 1);
    setTimeout(() => validateForm(), 0);
  };

  const handleRemoveCodelist = () => {
    setFieldValue("codelistType1", undefined);
    setFieldValue("codelist1", undefined);
    setCodelistCount(codelistCount - 1);
    setTimeout(() => validateForm(), 0);
  };

  const handleNextPage = () => {
    validateForm().then(() => {
      if (isValid) {
        nextStep();
      }
    });
  };

  return (
    <div className="grid grid-cols-2 gap-8 items-start">
      <div className="flex flex-col items-start gap-y-8">
        {Array(codelistCount)
          .fill(0)
          .map((_, i) => (
            <SelectCodelist
              // eslint-disable-next-line react/no-array-index-key
              key={i}
              description={
                i === 0
                  ? "Choose a codelist type, then search for a codelist"
                  : "Add another codelist to the request"
              }
              id={i}
              label={i === 0 ? "Select a codelist" : "Select another codelist"}
            />
          ))}
        {codelistCount < 2 ? (
          <button onClick={handleAddCodelist} type="button">
            Add another codelist
          </button>
        ) : (
          <button onClick={handleRemoveCodelist} type="button">
            Remove second codelist
          </button>
        )}

        <div id="my-radio-group">Select a frequency to group events by</div>
        <div aria-labelledby="my-radio-group" role="group">
          <label htmlFor="monthly">
            <Field id="monthly" name="picked" type="radio" value="monthly" />
            Monthly
          </label>
          <label htmlFor="quarterly">
            <Field id="quarterly" name="picked" type="radio" value="quarterly" />
            Quarterly
          </label>
          <label htmlFor="yearly">
            <Field id="yearly" name="picked" type="radio" value="yearly" />
            Yearly
          </label>
        </div>

        <button onClick={handleNextPage} type="button">
          Next
        </button>
      </div>
      {/* Show a section below the Combobox explaining about codelists */}
      <div className="max-h-fit border-l-2 border-l-oxford-200 bg-oxford-50 rounded pl-4 pr-2 py-4 mt-4 text-sm text-slate-800">
        <ul className="list-disc pl-4 grid grid-flow-row gap-2">
          <li>
            <a
              className="text-oxford-600 font-semibold underline underline-offset-1 transition-colors hover:text-oxford-500 hover:no-underline focus:text-oxford-700 focus:no-underline"
              href="https://www.opencodelists.org/docs/#what-is-a-codelist"
              rel="noopener noreferrer"
              target="_blank"
            >
              What is a codelist?
            </a>
          </li>
          <li>
            <a
              className="text-oxford-600 font-semibold underline underline-offset-1 transition-colors hover:text-oxford-500 hover:no-underline focus:text-oxford-700 focus:no-underline"
              href="https://www.snomed.org/"
              rel="noopener noreferrer"
              target="_blank"
            >
              What is SNOMED CT?
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Step1;

Step1.propTypes = {
  codelistCount: number.isRequired,
  setCodelistCount: func.isRequired,
};
