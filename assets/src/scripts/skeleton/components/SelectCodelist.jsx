import { Field, useFormikContext } from "formik";
import { number, string } from "prop-types";
import React, { Fragment } from "react";
import { usePageData } from "../context/page-data-context";
import codelists from "../data/codelists.json";
import { classNames } from "../utils";
import Combobox from "./Combobox";

function SelectCodelist({ description, label, id }) {
  const codelist = `codelist${id}`;
  const codelistType = `codelistType${id}`;
  const codelistGroup = `codelistGroup${id}`;

  const {
    state: { data },
  } = usePageData();
  const {
    errors,
    setFieldError,
    setFieldTouched,
    setFieldValue,
    touched,
    validateForm,
    values,
  } = useFormikContext();

  const radioButtonChange = (item) => {
    if (item.id !== values[codelistType]) {
      setFieldValue(codelist, "");
      setFieldTouched(codelist, false);
    }
  };

  const handleSelectedItemChange = (item) => {
    setFieldError(codelist, undefined);
    setFieldValue(codelist, item?.selectedItem || undefined);
    setFieldTouched(codelist, true);
    setTimeout(() => validateForm(), 0);
  };

  return (
    <div aria-labelledby={codelistGroup} className="w-full mt-6" role="group">
      <h2 className="text-lg font-bold" id={codelistGroup}>
        {label}
      </h2>
      <p className="text-base text-slate-700">{description}</p>
      <fieldset className="mt-2">
        <legend className="sr-only">Select a codelist type</legend>
        <div className="grid grid-cols-2 gap-2">
          {codelists.map((item) => (
            <label
              key={item.name}
              className={classNames(
                "border rounded-md shadow-sm py-2 px-1 flex items-center justify-center text-sm font-semibold sm:flex-1 cursor-pointer focus:outline-none",
                item.id === values[codelistType]
                  ? "ring-2 ring-oxford-500"
                  : null
              )}
              htmlFor={codelistType + item.id}
            >
              <Field
                className="sr-only"
                id={codelistType + item.id}
                name={codelistType}
                onClick={() => radioButtonChange(item)}
                type="radio"
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
              <Combobox
                choices={data}
                data={{
                  choices: "",
                  errors: "",
                  hint: "",
                  id: "",
                  label: "",
                  name: "",
                }}
                errors={[""]}
                handleSelectedItemChange={(i) => handleSelectedItemChange(i)}
                initialSelectedItem={values[codelist] || null}
              />
              {errors[codelist] && touched[codelist] ? (
                // eslint-disable-next-line no-console
                <div>{console.log(errors[codelist])}</div>
              ) : null}
            </>
          ) : null}
        </Fragment>
      ))}
    </div>
  );
}

export default SelectCodelist;

SelectCodelist.propTypes = {
  description: string.isRequired,
  label: string.isRequired,
  id: number.isRequired,
};
