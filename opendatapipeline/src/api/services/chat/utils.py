class ChatUtils:
    
    def get_cwf_and_files(self, history):
        cwf = {}
        files = []
        try:
            for item in history:
                output = item.get("output")
                parameters = item.get("parameters")
                if item.get("function") == "delete_files":
                    target_source_id = parameters.get("source_id")
                    for i, f in enumerate(files):
                        if f["source_id"] == target_source_id:
                            files.pop(i)
                            break
                    if cwf["source_id"] == target_source_id:
                        del cwf["source_id"]
                        del cwf["alias"]
                elif output and item.get("function") == 'pytool':
                    for file in output:
                        files.append({
                            "source_id":file.get("source_id"),
                            "alias" : file.get("dataframe_alias")
                        })
                        cwf.update(**{
                            "source_id":file.get("source_id"),
                            "alias" : file.get("dataframe_alias")
                        })
                elif item.get("function") == 'data_migration':
                    pass
                elif output and output.get("source_id"):
                    files.append({
                        "source_id":output.get("source_id"),
                        "alias" : output.get("dataframe_alias")
                    })
                    cwf.update(**{
                            "source_id":output.get("source_id"),
                            "alias" : output.get("dataframe_alias")
                        })
                else:
                    cwf.update(**{
                            "source_id":parameters.get("source_id"),
                            "alias" : parameters.get("dataframe_alias")
                        })
            return cwf, files
        except Exception as e:
            raise(e)
    

                
            