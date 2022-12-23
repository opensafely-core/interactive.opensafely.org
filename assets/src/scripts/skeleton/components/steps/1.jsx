import { Field, useFormikContext } from "formik";
import { func, number } from "prop-types";
import React from "react";
import { useWizard } from "react-use-wizard";
import { classNames } from "../../utils";
import InputFeedback from "../InputFeedback";
import SelectCodelist from "../SelectCodelist";

function Step1({ codelistCount, setCodelistCount }) {
  const { isValid, setFieldValue, validateForm, touched, errors } =
    useFormikContext();
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
    <div className="grid grid-cols-2 gap-x-8 items-start">
      <div className="flex flex-col items-start">
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
          <button
            className={classNames(
              "inline-flex items-center justify-center rounded-md border border-transparent shadow-sm transition-buttons duration-200 px-4 py-2 text-sm font-medium bg-oxford-600 text-white",
              "hover:bg-oxford-700 hover:shadow-lg",
              "focus:bg-oxford-700 focus:ring-oxford-500 focus:ring-offset-white focus:outline-none focus:ring-2 focus:ring-offset-2"
            )}
            onClick={handleAddCodelist}
            type="button"
          >
            Add another codelist
          </button>
        ) : (
          <button
            className={classNames(
              "inline-flex items-center justify-center rounded-md border border-transparent shadow-sm transition-buttons duration-200 px-4 py-2 text-sm font-medium bg-red-600 text-white",
              "hover:bg-red-700 hover:shadow-lg",
              "focus:bg-red-700 focus:ring-red-500 focus:ring-offset-white focus:outline-none focus:ring-2 focus:ring-offset-2"
            )}
            onClick={handleRemoveCodelist}
            type="button"
          >
            Remove second codelist
          </button>
        )}

        <fieldset className="flex flex-col items-start mt-12 mb-6">
          <legend className="text-lg font-bold mb-1">
            Select a frequency to group events by{" "}
            <span className="text-red-700">*</span>
          </legend>
          <label
            className="inline-flex flex-row gap-x-2 items-center cursor-pointer mb-1"
            htmlFor="monthly"
          >
            <Field
              className="h-4 w-4 border-gray-300 text-oxford-600 focus:ring-oxford-500"
              id="monthly"
              name="frequency"
              type="radio"
              value="monthly"
            />
            Monthly
          </label>
          <label
            className="inline-flex flex-row gap-x-2 items-center cursor-pointer mb-1"
            htmlFor="quarterly"
          >
            <Field
              className="h-4 w-4 border-gray-300 text-oxford-600 focus:ring-oxford-500"
              id="quarterly"
              name="frequency"
              type="radio"
              value="quarterly"
            />
            Quarterly
          </label>
          <label
            className="inline-flex flex-row gap-x-2 items-center cursor-pointer"
            htmlFor="yearly"
          >
            <Field
              className="h-4 w-4 border-gray-300 text-oxford-600 focus:ring-oxford-500"
              id="yearly"
              name="frequency"
              type="radio"
              value="yearly"
            />
            Yearly
          </label>
          {touched.frequency && errors.frequency ? (
            <InputFeedback error={errors.frequency} />
          ) : null}
        </fieldset>

        <button
          className={classNames(
            "inline-flex items-center justify-center rounded-md border border-transparent shadow-sm transition-buttons duration-200 px-4 py-2 text-sm font-medium bg-oxford-600 text-white",
            "hover:bg-oxford-700 hover:shadow-lg",
            "focus:bg-oxford-700 focus:ring-oxford-500 focus:ring-offset-white focus:outline-none focus:ring-2 focus:ring-offset-2",
            !isValid ? "opacity-75 cursor-not-allowed !bg-slate-700" : null
          )}
          // disabled={!isValid}
          onClick={handleNextPage}
          type="button"
        >
          Next
        </button>
      </div>
      {/* Show a section below the Combobox explaining about codelists */}
      <div className="max-h-fit border-l-2 border-l-oxford-200 bg-oxford-50 shadow pl-4 pr-2 py-4 mt-4 text-sm text-slate-800">
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
