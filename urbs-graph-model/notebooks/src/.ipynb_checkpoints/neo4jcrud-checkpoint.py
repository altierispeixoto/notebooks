from neo4j import GraphDatabase


class UrbsNeo4JDatabase(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_bus_company(self, company_code, company_name):
        with self._driver.session() as session:
            return session.run("CREATE (c:Company) "
                               " SET c.company_code = $company_code , c.company_name=$company_name RETURN id(c)",
                               company_code=company_code, company_name=company_name).single().value()

    def create_bus_category(self, category_code, category_name):
        with self._driver.session() as session:
            return session.run("CREATE (bc:BusCategory) "
                               " SET bc.category_code = $category_code , bc.category_name=$category_name RETURN id(bc)",
                               category_code=category_code, category_name=category_name).single().value()

    def create_bus_stop(self, name, number, type, latitude, longitude):
        with self._driver.session() as session:
            return session.run("CREATE (bs:BusStop) "
                               " SET bs.name = $name , bs.number=$number , bs.type=$type, "
                               "bs.latitude=$latitude, bs.longitude=$longitude return id(bs)",
                               name=name, number=number, type=type, latitude=latitude,
                               longitude=longitude).single().value()

    def create_bus_lines(self, start_point, end_point, line_code, line_way, service_category, line_name, color_name,
                         card_only):
        cipher_query = 'MATCH(bss: BusStop {number: $start_point}), (bse: BusStop {number: $end_point}) ' \
                       'CREATE(bss) - [: NEXT_STOP {' \
                       '  line_code: $line_code' \
                       ' ,line_way: $line_way' \
                       ' ,service_category: $service_category' \
                       ' ,line_name: $line_name' \
                       ' ,color_name: $color_name' \
                       ' ,card_only: $card_only' \
                       '}]->(bse)'

        with self._driver.session() as session:
            return session.run(cipher_query,
                               start_point=start_point
                               , end_point=end_point
                               , line_code=line_code
                               , line_way=line_way
                               , service_category=service_category
                               , line_name=line_name
                               , color_name=color_name
                               , card_only=card_only)

    def create_bus(self, vehicle):
        with self._driver.session() as session:
            return session.run("CREATE (b:Bus) "
                               " SET b.vehicle = $vehicle RETURN id(b)",
                               vehicle=vehicle).single().value()

    def create_position(self, vehicle, latitude, longitude,line_code, dt_event):
        with self._driver.session() as session:
            return session.run('CREATE (p:Position) '
                               ' SET p.vehicle = $vehicle '
                               ', p.coordinates = point({ latitude:toFloat($latitude),longitude:toFloat($longitude) }) '
                               ', p.dt_event = $dt_event '
                               ', p.line_code = $line_code '
                               ' RETURN id(p)',
                               vehicle=vehicle, latitude=latitude, longitude=longitude,
                               dt_event=str(dt_event),line_code=line_code).single().value()
    
    
    def connect_events(self,vehicle,line_code):
        
        connect_evt = "MATCH (p:Position {vehicle: $vehicle,line_code: $line_code }) " \
                       "WITH p ORDER BY p.dt_event DESC " \
                       "WITH collect(p) as entries "  \
                       "FOREACH(i in RANGE(0, size(entries)-2) | " \
                       "FOREACH(e1 in [entries[i]] | " \
                       "FOREACH(e2 in [entries[i+1]] | " \
                       "MERGE (e2)-[ :MOVES_TO ]->(e1)))) "

        with self._driver.session() as session:
            return session.run(connect_evt, vehicle=vehicle,line_code=line_code)
        
    #
    # def create_principio_ativo(self, name_pt_br, name_en, drugbank_id, description_en, description_pt_br):
    #     with self._driver.session() as session:
    #         return session.run(
    #             "MERGE (d:Drug "
    #             "{name_pt_br: $name_pt_br"
    #             ",name_en: $name_en,"
    #             " drugbank_id:$drugbank_id,"
    #             " drugbank_description_en:$description_en,"
    #             " description_pt_br:$description_pt_br}"
    #             ") RETURN id(d)",
    #             name_pt_br=name_pt_br, name_en=name_en, drugbank_id=drugbank_id,
    #             description_en=description_en, description_pt_br=description_pt_br).single().value()
    #
    # def create_relationship_drug_disease(self, drugbank_id, disease):
    #     with self._driver.session() as session:
    #         return session.run("MATCH (p:Patologia),(d:Drug) "
    #                            "WHERE p.disease = $disease and  d.drugbank_id = $drugbank_id "
    #                            "CREATE (d)-[r:indication "
    #                            "{ nome: p.disease + ' <-> ' + d.name_pt_br}]->(p) "
    #                            "RETURN type(r), r.nome",
    #                            disease=disease, drugbank_id=drugbank_id)
    #
    # def create_relationship_counter_indication_drug_disease(self, drugbank_id, disease):
    #     with self._driver.session() as session:
    #         return session.run("MATCH (p:Patologia),(d:Drug) "
    #                            "WHERE p.disease = $disease and  d.drugbank_id = $drugbank_id "
    #                            "CREATE (d)-[r:counter_indication "
    #                            "{ nome: p.disease + ' <-> ' + d.name_pt_br}]->(p) "
    #                            "RETURN type(r), r.nome",
    #                            disease=disease, drugbank_id=drugbank_id)
    #
    # def create_drug_interaction_relationship(self,drugbank_interaction_id,drugbank_id, description_pt_br):
    #     with self._driver.session() as session:
    #         return session.run("MATCH (d0:Drug),(d:Drug) "
    #                            "WHERE d0.drugbank_id = $drugbank_interaction_id and  d.drugbank_id = $drugbank_id "
    #                            "CREATE (d0)-[r:drug_interaction "
    #                            "{ description: $description_pt_br}]->(d) "
    #                            "RETURN type(r)",
    #                            drugbank_interaction_id=drugbank_interaction_id, drugbank_id=drugbank_id
    #                            , description_pt_br=description_pt_br)
    #
    #
    def delete_all(self):
        with self._driver.session() as session:
            return session.run("MATCH (n) DETACH DELETE n").single()
