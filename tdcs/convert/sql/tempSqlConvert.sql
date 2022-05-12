/* Biz: com.sktps.rmt.pfmbase.db.DACCPFM01300.saveEwsCrdtMgmt  */
/* IO: 배진우,2018-05-17T14:43:27(배진우,2018-05-17T14:43:27) */
MERGE INTO TACC_EWS_CRDT_UPLOAD A USING 

    (SELECT #{CRDT_TGT_ID} CRDT_TGT_ID
         , #{ACC_MTH} ACC_MTH
         , TO_NUMBER(#{SEQ}) SEQ 
      FROM dual 
    ) B ON ( a.CRDT_TGT_ID = b.CRDT_TGT_ID AND a.ACC_MTH = b.ACC_MTH AND a.SEQ = b.SEQ ) 
WHEN MATCHED THEN 
       UPDATE 
              SET UPD_CNT = nvl(upd_cnt, 0) + 1 
            , MOD_DTM     = TO_CHAR(SYSDATE, 'yyyymmddhh24miss') 
            , MOD_USER_ID = #onlineContext.userInfo.loginId# 
            , SALE_MTH_QTY = #{SALE_MTH_QTY} 
            , AVG_SALE_RATE = #{AVG_SALE_RATE} 
            , USE_RATE_MOSU = #{USE_RATE_MOSU} 
            , USE_RATE_JASU = #{USE_RATE_JASU} 
            , CRDT_USE_RATE = #{CRDT_USE_RATE} 
            , FDMI_SALE_QTY = #{FDMI_SALE_QTY} 
            , FDMI_EXCP_CASE = #{FDMI_EXCP_CASE} 
            , FDMI_USE_RATE  = #{FDMI_USE_RATE} 
            , EVENT_QTY      = #{EVENT_QTY} 
            , BOND_BAMT      = #{BOND_BAMT} 
            , THR_STOP_SALE_QTY = #{THR_STOP_SALE_QTY} 
            , THR_STOP_CANC_QTY = #{THR_STOP_CANC_QTY} 
            , THR_STOP_CANC_RATE = #{THR_STOP_CANC_RATE} 
            , NM_STEAL_QTY       = #{NM_STEAL_QTY} 
            , NON_OCCR_QTY       = #{NON_OCCR_QTY} 
            , DIS_HLD_MOSU       = #{DIS_HLD_MOSU} 
            , DIS_HLD_JASU       = #{DIS_HLD_JASU} 
            , DIS_HLD_RATE       = #{DIS_HLD_RATE} 
            , CIA_COMP_RATE      = #{CIA_COMP_RATE} 
            , CIA_RETURN_QTY     = #{CIA_RETURN_QTY} 
            , DEAL_EFF_MTH       = REPLACE(#{DEAL_EFF_MTH}, '-', '') 
            , DEAL_MTH_QTY       = #{DEAL_MTH_QTY} 
            , VOC_QTY            = #{VOC_QTY} 
            , MIN_CRDT_USE_GRADE = #{MIN_CRDT_USE_GRADE} 
            , MIN_FDMI_GRADE     = #{MIN_FDMI_GRADE} 
            , MIN_EVENT_GRADE    = #{MIN_EVENT_GRADE} 
            , MIN_BOND_BAMT_GRADE = #{MIN_BOND_BAMT_GRADE} 
            , MIN_THR_STOP_GRADE  = #{MIN_THR_STOP_GRADE} 
            , MIN_NM_STEAL_GRADE  = #{MIN_NM_STEAL_GRADE} 
            , MIN_NON_OCCR_GRADE  = #{MIN_NON_OCCR_GRADE} 
            , MIN_DIS_HLD_GRADE   = #{MIN_DIS_HLD_GRADE} 
            , MIN_CIA_COMP_GRADE  = #{MIN_CIA_COMP_GRADE} 
            , MIN_ETC_RM_GRADE    = #{MIN_ETC_RM_GRADE} 
            , MIN_DEAL_EFF_GRADE  = #{MIN_DEAL_EFF_GRADE} 
            , MIN_VOC_GRADE       = #{MIN_VOC_GRADE} 
            , TOT_MIN_GRADE       = #{TOT_MIN_GRADE} 
            , EWS_RANK            = #{EWS_RANK} WHEN NOT MATCHED THEN 
       INSERT 
              ( 
                  CRDT_TGT_ID 
                , ACC_MTH 
                , SEQ 
                , SALE_MTH_QTY 
                , AVG_SALE_RATE 
                , USE_RATE_MOSU 
                , USE_RATE_JASU 
                , CRDT_USE_RATE 
                , FDMI_SALE_QTY 
                , FDMI_EXCP_CASE 
                , FDMI_USE_RATE 
                , EVENT_QTY 
                , BOND_BAMT 
                , THR_STOP_SALE_QTY 
                , THR_STOP_CANC_QTY 
                , THR_STOP_CANC_RATE 
                , NM_STEAL_QTY 
                , NON_OCCR_QTY 
                , DIS_HLD_MOSU 
                , DIS_HLD_JASU 
                , DIS_HLD_RATE 
                , CIA_COMP_RATE 
                , CIA_RETURN_QTY 
                , DEAL_EFF_MTH 
                , DEAL_MTH_QTY 
                , VOC_QTY 
                , MIN_CRDT_USE_GRADE 
                , MIN_FDMI_GRADE 
                , MIN_EVENT_GRADE 
                , MIN_BOND_BAMT_GRADE 
                , MIN_THR_STOP_GRADE 
                , MIN_NM_STEAL_GRADE 
                , MIN_NON_OCCR_GRADE 
                , MIN_DIS_HLD_GRADE 
                , MIN_CIA_COMP_GRADE 
                , MIN_ETC_RM_GRADE 
                , MIN_DEAL_EFF_GRADE 
                , MIN_VOC_GRADE 
                , TOT_MIN_GRADE 
                , EWS_RANK 
                , DEL_YN 
                , UPD_CNT 
                , INS_DTM 
                , INS_USER_ID 
                , MOD_DTM 
                , MOD_USER_ID 
              ) 
              VALUES 
              ( 
                  #{CRDT_TGT_ID} 
                , #{ACC_MTH} 
                , TO_NUMBER(#{SEQ}) 
                , #{SALE_MTH_QTY} 
                , #{AVG_SALE_RATE} 
                , #{USE_RATE_MOSU} 
                , #{USE_RATE_JASU} 
                , #{CRDT_USE_RATE} 
                , #{FDMI_SALE_QTY} 
                , #{FDMI_EXCP_CASE} 
                , #{FDMI_USE_RATE} 
                , #{EVENT_QTY} 
                , #{BOND_BAMT} 
                , #{THR_STOP_SALE_QTY} 
                , #{THR_STOP_CANC_QTY} 
                , #{THR_STOP_CANC_RATE} 
                , #{NM_STEAL_QTY} 
                , #{NON_OCCR_QTY} 
                , #{DIS_HLD_MOSU} 
                , #{DIS_HLD_JASU} 
                , #{DIS_HLD_RATE} 
                , #{CIA_COMP_RATE} 
                , #{CIA_RETURN_QTY} 
                , REPLACE(#{DEAL_EFF_MTH}, '-', '') 
                , #{DEAL_MTH_QTY} 
                , #{VOC_QTY} 
                , #{MIN_CRDT_USE_GRADE} 
                , #{MIN_FDMI_GRADE} 
                , #{MIN_EVENT_GRADE} 
                , #{MIN_BOND_BAMT_GRADE} 
                , #{MIN_THR_STOP_GRADE} 
                , #{MIN_NM_STEAL_GRADE} 
                , #{MIN_NON_OCCR_GRADE} 
                , #{MIN_DIS_HLD_GRADE} 
                , #{MIN_CIA_COMP_GRADE} 
                , #{MIN_ETC_RM_GRADE} 
                , #{MIN_DEAL_EFF_GRADE} 
                , #{MIN_VOC_GRADE} 
                , #{TOT_MIN_GRADE} 
                , #{EWS_RANK} 
                , 'N' 
                , 0 
                , TO_CHAR(SYSDATE, 'yyyymmddhh24miss') 
                , #onlineContext.userInfo.loginId# 
                , TO_CHAR(SYSDATE, 'yyyymmddhh24miss') 
                , #onlineContext.userInfo.loginId# 
              )