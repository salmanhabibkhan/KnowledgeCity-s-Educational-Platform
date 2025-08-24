import { ArnPrincipal } from "aws-cdk-lib/aws-iam";
import { ApplicationTeam } from "@aws-quickstart/eks-blueprints";

export class KcApplicationTeam extends ApplicationTeam {
    constructor(name: string, accountID: string) {
        super({
            name: name,
            // aws iam create-user --user-name application
            users: [new ArnPrincipal(`arn:aws:iam::${accountID}:user/application`)]
        });
    }
}
