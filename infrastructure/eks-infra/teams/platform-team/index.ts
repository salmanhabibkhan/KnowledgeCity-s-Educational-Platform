import { ArnPrincipal } from "aws-cdk-lib/aws-iam";
import { PlatformTeam } from '@aws-quickstart/eks-blueprints';

export class KcPlatformTeam extends PlatformTeam {
    constructor(accountID: string) {
        super({
            name: 'platform',
            // aws iam create-user --user-name platform
            users: [new ArnPrincipal(`arn:aws:iam::${accountID}:user/platform`)]
        })
    }
}
