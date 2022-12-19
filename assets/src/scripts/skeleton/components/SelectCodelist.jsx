import { Field, useFormikContext } from "formik";
import React, { Fragment } from "react";
import codelists from "../data/codelists.json";
import { classNames } from "../utils";

function SelectCodelist({ id }) {
  const codelist = "codelist" + id;
  const codelistType = "codelistType" + id;
  const codelistGroup = "codelistGroup" + id;

  const {
    errors,
    isValid,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();

  const radioButtonChange = ({ id }) => {
    if (id !== values[codelistType]) {
      setFieldValue(codelist, "");
      setFieldTouched(codelist, false);
    }
  };

  return (
    <div role="group" aria-labelledby={codelistGroup}>
      <h2 id={codelistGroup}>Select a codelist</h2>
      <fieldset>
        <legend className="sr-only">Select a codelist type</legend>
        <div className="grid grid-cols-2 gap-2">
          {codelists.map((item) => (
            <label
              key={item.name}
              className={classNames(
                "border rounded-md py-2 px-1 flex items-center justify-center text-sm font-semibold sm:flex-1 cursor-pointer focus:outline-none",
                item.id === values[codelistType]
                  ? "ring-2 ring-oxford-500"
                  : null
              )}
              onClick={() => radioButtonChange({ id: item.id })}
            >
              <Field
                className="sr-only"
                type="radio"
                name={codelistType}
                value={item.id}
              />
              {item.name}
            </label>
          ))}
        </div>
      </fieldset>

      {errors[codelistType] && touched[codelistType] ? (
        <div>{errors[codelistType]}</div>
      ) : null}
      {codelists.map((item) => (
        <Fragment key={item.id}>
          {item.id === values[codelistType] ? (
            <>
              <Field as="select" name={codelist} id={codelist}>
                <option value="">Search for a codelist</option>
                <option value="test">Test1</option>
                <option value="test-2">Test2</option>
              </Field>
              {errors[codelist] && touched[codelist] ? (
                <div>{errors[codelist]}</div>
              ) : null}
            </>
          ) : null}
        </Fragment>
      ))}
    </div>
  );
}

export default SelectCodelist;
